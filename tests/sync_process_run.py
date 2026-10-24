# This file starts the sync carrier as a process of its own against a journal server and a team server, so it is not in the default run: python3 -m pytest tests/sync_process_run.py
import json
import os
import re
import signal
import socket
import subprocess
import sys
import time
from pathlib import Path
from urllib.request import Request as HttpRequest, urlopen

import pytest

from journal.app import App
from journal.config import Config
from journal.engine.agent_launcher import AgentLauncher
from journal.repositories.outgoing_changes import OutgoingChanges
from journal.support.caller import Caller
from journal.support.supervisor_socket import SupervisorSocket
from journal.sync.carrier_beat import CarrierBeat
from journal.sync.sync_secret import SECRET_FILE
from journal.sync.sync_start import SyncStart
from journal.sync.sync_status import SyncStatus
from journal.sync.team_account import TeamAccount
from journal.sync.team_chat_branch import TEAM_CHAT
from sync_server.account import ADMIN
from sync_server.login_request import LoginRequest
from sync_server.team_server import TeamServer

from main_journal import main_journal

PACKAGE = Path(__file__).resolve().parents[1] / "src"
USER = Caller.user("main")


@pytest.fixture(scope="module")
def boot():
    return booted


def booted(root: Path, patch: pytest.MonkeyPatch) -> App:
    patch.setattr(Config, "status_home", property(lambda self: root / "status"))
    app = main_journal(Config(root, port=0))
    app.runtime().start()
    return app


def eventually(check, seconds: float) -> bool:
    deadline = time.monotonic() + seconds
    while time.monotonic() < deadline:
        if check():
            return True
        time.sleep(0.1)
    return check()


def carrier(app: App) -> subprocess.Popen:
    environ = {**os.environ, "JOURNAL_ROOT": str(app.config.root), "PYTHONPATH": str(PACKAGE), "PYTHONFAULTHANDLER": "1", "JOURNAL_ENV": "main"}
    return subprocess.Popen([sys.executable, str(PACKAGE / "journal.py"), "sync"], env=environ, stdout=subprocess.DEVNULL, stderr=open(app.config.root / "carrier.log", "a"))


def test_the_carrier_in_a_process_of_its_own_sends_the_journals_changes_once_and_takes_the_teams_through_the_local_doors(app: App):
    folder = app.config.root / "team-server"
    folder.mkdir()
    team = TeamServer(folder)
    team.accounts.create("ada@example.com", "Ada", "correct horse battery", ADMIN, 1.0)
    server = team.started("127.0.0.1", 0)
    answer = team.logins.answer(LoginRequest("ada@example.com", "correct horse battery", "ada-laptop"), "127.0.0.1")
    account = app.container.get(TeamAccount)
    account.write({"address": f"http://127.0.0.1:{server.server_address[1]}", "token": answer.token, "device": answer.device_id, "sequence": 0})
    app.server()
    app.container.get(OutgoingChanges).clear()
    process = carrier(app)
    try:
        made = app.console().run(["task", "create", "sent by the carrier"], USER)
        assert made.code == 0, made.error
        titles = lambda: [row.fields.get("title") for row in team.log.copied_rows() if row.row_table == "tasks"]
        sent = eventually(lambda: "sent by the carrier" in titles(), 20)
        if not sent:
            process.send_signal(signal.SIGABRT)
            process.wait(10)
        assert sent, f"alive {process.poll() is None}, waiting {len(app.container.get(OutgoingChanges).waiting())}, team {titles()}, log {(app.config.root / 'carrier.log').read_text()[:2500]}"
        process.send_signal(signal.SIGKILL)
        process.wait(10)
        status = app.container.get(SyncStatus)
        assert eventually(lambda: status.line() == "Not connected: the sync process is not running", 15), "a killed carrier shows as not connected within seconds"
        app.console().run(["task", "create", "made while the carrier was down"], USER)
        process = carrier(app)
        assert eventually(lambda: "made while the carrier was down" in titles(), 20), "a carrier started again sends what waited"
        assert titles().count("made while the carrier was down") == 1, "and sends it once"
        assert eventually(lambda: app.container.get(OutgoingChanges).waiting() == [], 10), "the queue empties as the team takes it"
    finally:
        process.send_signal(signal.SIGTERM)
        process.wait(10)
        account.left(0)
        server.shutdown()


def git(*arguments: str) -> None:
    subprocess.run(["git", *arguments], capture_output=True, check=True, timeout=30)


def clean_environ(root: Path, environment: str, home: Path) -> dict[str, str]:
    """The test's own environment without the journal and agent this run is started under, for a journal of its own on root."""
    kept = {key: value for key, value in os.environ.items() if not key.startswith(("JOURNAL_", "SUPERVISOR_", "CLAUDE")) and key != "AGENT_JOURNAL_ACTIVE"}
    return {**kept, "JOURNAL_ROOT": str(root), "JOURNAL_ENV": environment, "JOURNAL_PORT": "0", "HOME": str(home), "PYTHONPATH": str(PACKAGE)}


def supervised(root: Path, environment: str, home: Path, services: list[dict]) -> tuple[subprocess.Popen, str]:
    """A real supervisor for one environment of root, started from a launch file as the launcher writes it, with cat as the agent in front; the supervisor and its socket."""
    runtime = root / ".journal" / "runtime"
    environ = {**clean_environ(root, environment, home), "JOURNAL_LAUNCH": f"test-{environment}"}
    socket_path = str(Path("/tmp") / f"journal-{os.getuid()}" / f"t{os.getpid()}-{environment}.sock")
    launch = {"launch": f"test-{environment}", "front": {"command": ["cat"], "resume": [], "folder": str(root), "env": environ}, "services": services, "socket": socket_path, "owner": os.getpid(), "announce": str(runtime / "inboxes" / environment), "screen": str(runtime / "screens" / f"{environment}.out")}
    path = runtime / "launches" / f"{environment}.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    (runtime / "inboxes").mkdir(exist_ok=True)
    path.write_text(json.dumps(launch))
    process = subprocess.Popen([sys.executable, "-m", "supervisor", str(path)], cwd=root, env=environ, stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=open(runtime / f"supervisor-{environment}.err", "a"))
    return process, socket_path


def processes(socket_path: str) -> dict[str, dict]:
    try:
        with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as link:
            link.settimeout(5)
            link.connect(socket_path)
            link.sendall(b'{"verb": "list"}\n')
            return {process["name"]: process for process in json.loads(link.makefile("rb").readline())["processes"]}
    except (OSError, ValueError, KeyError):
        return {}


def journal_post(root: Path, environment: str, path: str, body: dict, headers: dict[str, str] = {}) -> dict:
    port = Config(root).stored_port()[0]
    request = HttpRequest(f"http://127.0.0.1:{port}{path}", data=json.dumps(body).encode(), method="POST", headers={"Content-Type": "application/json", "X-Journal-Env": environment, **headers})
    with urlopen(request, timeout=10) as answer:
        return json.loads(answer.read() or b"{}")


def answering(root: Path) -> bool:
    port = Config(root).stored_port()
    try:
        with urlopen(f"http://127.0.0.1:{port[0]}/journal/health", timeout=1):
            return True
    except (OSError, IndexError):
        return False


def ended(process: subprocess.Popen) -> None:
    if process.poll() is None:
        process.terminate()
    try:
        process.wait(20)
    except subprocess.TimeoutExpired:
        process.kill()
        process.wait(5)


def test_the_supervisor_runs_the_carrier_as_the_journals_child_through_a_restart_and_types_a_teammates_team_chat_message(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    monkeypatch.delenv("JOURNAL_ENV", raising=False)
    root, clone, home = tmp_path / "a", tmp_path / "b", tmp_path / "home"
    home.mkdir()
    git("init", "-q", str(root))
    git("-C", str(root), "-c", "user.name=Ada", "-c", "user.email=ada@example.com", "commit", "-q", "--allow-empty", "-m", "first")
    git("-C", str(root), "config", "user.name", "Ada")
    git("-C", str(root), "config", "user.email", "ada@example.com")
    git("clone", "-q", str(root), str(clone))
    (tmp_path / "team-server").mkdir()
    team = TeamServer(tmp_path / "team-server")
    server = team.started("127.0.0.1", 0)
    address = f"http://127.0.0.1:{server.server_address[1]}"
    bob = booted(clone, monkeypatch)
    started: list[subprocess.Popen] = []
    pids: set[int] = set()
    try:
        # the root is prepared in-process without its runtime, its own sync stopped once the join starts it, since the supervised server is the journal here
        ada = main_journal(Config(root, port=0))
        joined = ada.console().run(["team", "join", address, "--email", "ada@example.com", "--name", "Ada", "--password", "correct horse battery"], USER)
        assert joined.code == 0, joined.text + joined.error
        ada.container.get(SyncStart).stopped()
        invitation = ada.console().run(["team", "invite", "bob@example.com"], USER).text
        bob_url = re.search(r"(http\S+/join\?code=\S+)", invitation).group(1)
        joined_bob = bob.console().run(["team", "join", bob_url, "--email", "bob@example.com", "--name", "Bob", "--password", "correct horse battery", "--replace-mine"], USER)
        assert joined_bob.code == 0, joined_bob.text + joined_bob.error
        # the claim's launcher would start the Team chat's agent as a supervisor with no journal of its own: the test starts that supervisor itself below
        monkeypatch.setattr(AgentLauncher, "start", lambda self, environment, agent: 1)
        claimed = ada.console().run(["team", "claim"], USER)
        assert claimed.code == 0, claimed.text + claimed.error
        journal_service = {"name": "journal", "command": [sys.executable, str(PACKAGE / "journal.py"), "serve"], "folder": str(root), "env": clean_environ(root, "main", home), "log": str(root / ".journal" / "runtime" / "server.log")}
        main, main_socket = supervised(root, "main", home, [journal_service])
        started.append(main)
        logs = lambda: "\n".join(f"{path.name}: {path.read_text()[-2000:]}" for path in (root / ".journal" / "runtime").glob("*.log") if path.is_file())
        assert eventually(lambda: answering(root), 60), logs()
        beat = CarrierBeat(Config(root))
        titles = lambda: [row.fields.get("text") for row in team.log.copied_rows() if row.row_table == "messages"]
        faults: set[str] = set()

        def carried() -> dict:
            listed = processes(main_socket)
            for process in listed.values():
                pids.add(process["pid"])
            if beat.path.is_file():
                faults.add(json.loads(beat.path.read_text())["fault"])
            sync = listed.get("sync", {})
            return sync if sync.get("running") and beat.path.is_file() and json.loads(beat.path.read_text())["pid"] == sync["pid"] else {}

        assert eventually(carried, 30), logs()
        first = carried()
        assert first["parent"] == "journal", "the server's SyncStart starts the carrier as the journal's child service"
        journal_post(root, "main", "/journal/messages", {"text": "sent by the supervised carrier"})
        assert eventually(lambda: "sent by the supervised carrier" in titles(), 30), logs()

        os.kill(first["pid"], signal.SIGKILL)
        assert eventually(lambda: carried().get("pid") not in (None, first["pid"]), 30), "the supervisor starts a killed carrier again"
        revived = carried()
        assert revived["parent"] == "journal" and revived["restarts"] >= 1
        journal_post(root, "main", "/journal/messages", {"text": "sent by the revived carrier"})
        assert eventually(lambda: "sent by the revived carrier" in titles(), 30), logs()

        port, secret = Config(root).stored_port(), (root / ".journal" / "runtime" / SECRET_FILE).read_text()
        server_pid = processes(main_socket)["journal"]["pid"]
        assert SupervisorSocket.ask(main_socket, {"verb": "restart", "name": "journal", "after": 0}).success
        moved = lambda: Config(root).stored_port() != port and (root / ".journal" / "runtime" / SECRET_FILE).read_text() != secret and answering(root)
        assert eventually(lambda: bool(carried()) and moved() and processes(main_socket)["journal"]["pid"] != server_pid, 60), logs()
        journal_post(root, "main", "/journal/messages", {"text": "sent after the restart"})
        assert eventually(lambda: bool(carried()) and "sent after the restart" in titles(), 30), logs()
        assert titles().count("sent after the restart") == 1, "and sent once"
        assert faults == {""}, f"the carrier waits through a restart on a new port with a new secret and records no team fault: {faults}"
        assert "trying again" not in (root / ".journal" / "runtime" / "sync.log").read_text(), (root / ".journal" / "runtime" / "sync.log").read_text()[-3000:]

        chat, chat_socket = supervised(root, TEAM_CHAT, home, [])
        started.append(chat)
        assert eventually(lambda: "agent" in processes(chat_socket), 20)
        # the agent's hook script posts its session's start with the launch id its supervisor gave it
        journal_post(root, TEAM_CHAT, "/hooks/claude", {"hook_event_name": "SessionStart", "session_id": "chat1"}, {"X-Journal-Launch": f"test-{TEAM_CHAT}"})
        bob_port = bob.server().port
        ask = HttpRequest(f"http://127.0.0.1:{bob_port}/journal/messages", data=json.dumps({"text": "please run the tests"}).encode(), method="POST", headers={"Content-Type": "application/json", "X-Journal-Env": TEAM_CHAT})
        asked = json.loads(urlopen(ask, timeout=10).read())
        screen = root / ".journal" / "runtime" / "screens" / f"{TEAM_CHAT}.out"
        typed = lambda: screen.is_file() and f"new message {asked['id']}" in screen.read_bytes().decode(errors="replace")
        assert eventually(typed, 30), f"a teammate's Team chat message is typed to the agent through the server: {screen.read_bytes()[-2000:] if screen.is_file() else 'no screen'}; {logs()}"
    finally:
        for process in reversed(started):
            ended(process)
        for pid in pids - {0}:
            try:
                os.kill(pid, signal.SIGKILL)
            except ProcessLookupError:
                pass
        bob.container.get(SyncStart).stopped()
        bob.runtime().stop()
        server.shutdown()
