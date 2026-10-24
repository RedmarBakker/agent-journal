# This file starts a real supervisor running the journal server and the sync service side by side against a team server, so it is not in the default run: python3 -m pytest tests/sync_process_run.py
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
from journal.launcher.launch import Launch
from journal.support.caller import Caller
from journal.support.supervisor_socket import SupervisorSocket
from journal.sync.sync_secret import SECRET_FILE
from journal.sync.team_chat_branch import TEAM_CHAT
from sync_server.team_server import TeamServer

from carried_sync import CarriedSync
from main_journal import main_journal

PACKAGE = Path(__file__).resolve().parents[1] / "src"
USER = Caller.user("main")


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


def git(*arguments: str) -> None:
    subprocess.run(["git", *arguments], capture_output=True, check=True, timeout=30)


def clean_environ(root: Path, environment: str, home: Path) -> dict[str, str]:
    """The test's own environment without the journal and agent this run is started under, for a journal of its own on root."""
    kept = {key: value for key, value in os.environ.items() if not key.startswith(("JOURNAL_", "SUPERVISOR_", "CLAUDE")) and key != "AGENT_JOURNAL_ACTIVE"}
    return {**kept, "JOURNAL_ROOT": str(root), "JOURNAL_ENV": environment, "JOURNAL_PORT": "0", "HOME": str(home), "PYTHONPATH": str(PACKAGE)}


def services(root: Path, home: Path) -> list[dict]:
    """The journal server and the sync service as the launcher names them in its launch file, run on a port of their own."""
    launch, environ, runtime = Launch.parse(["claude", "--env", "main"], root), clean_environ(root, "main", home), root / ".journal" / "runtime"
    journal = {"name": "journal", "command": launch.journal_command(), "folder": str(root), "env": environ, "log": str(runtime / "server.log")}
    sync = {"name": "sync", "command": launch.sync_command(), "folder": str(root), "env": {**environ, "PYTHONPATH": str(launch.package)}, "log": str(runtime / "sync.log")}
    return [journal, sync]


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


def sync_line(root: Path) -> str:
    """The status bar's sync line as the running journal server gives it, or none while no server answers."""
    port = Config(root).stored_port()
    try:
        with urlopen(HttpRequest(f"http://127.0.0.1:{port[0]}/journal/sync", headers={"X-Journal-Env": "main"}), timeout=1) as answer:
            return json.loads(answer.read())["line"]
    except (OSError, IndexError, ValueError):
        return ""


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


def test_the_supervisor_runs_the_journal_and_the_sync_service_side_by_side_through_a_kill_and_a_restart_and_a_teammates_team_chat_message_is_typed(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
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
    bob_sync = CarriedSync(bob).started()
    started: list[subprocess.Popen] = []
    pids: set[int] = set()
    try:
        # the root is prepared in-process without its runtime, as two journals on one root wait for each other; the supervised server is the journal here
        ada = main_journal(Config(root, port=0))
        joined = ada.console().run(["team", "join", address, "--email", "ada@example.com", "--name", "Ada", "--password", "correct horse battery"], USER)
        assert joined.code == 0, joined.text + joined.error
        invitation = ada.console().run(["team", "invite", "bob@example.com"], USER).text
        bob_url = re.search(r"(http\S+/join\?code=\S+)", invitation).group(1)
        joined_bob = bob.console().run(["team", "join", bob_url, "--email", "bob@example.com", "--name", "Bob", "--password", "correct horse battery", "--replace-mine"], USER)
        assert joined_bob.code == 0, joined_bob.text + joined_bob.error
        # the claim's launcher would start the Team chat's agent as a supervisor with no journal of its own: the test starts that supervisor itself below
        monkeypatch.setattr(AgentLauncher, "start", lambda self, environment, agent: 1)
        claimed = ada.console().run(["team", "claim"], USER)
        assert claimed.code == 0, claimed.text + claimed.error
        main, main_socket = supervised(root, "main", home, services(root, home))
        started.append(main)
        runtime = root / ".journal" / "runtime"
        logs = lambda: "\n".join(f"{path.name}: {path.read_text()[-2000:]}" for path in runtime.glob("*.log") if path.is_file())
        assert eventually(lambda: answering(root), 60), logs()
        texts = lambda: [row.fields.get("text") for row in team.log.copied_rows() if row.row_table == "messages"]
        lines: set[str] = set()

        def running() -> dict[str, dict]:
            listed = processes(main_socket)
            pids.update(process["pid"] for process in listed.values())
            lines.add(sync_line(root))
            return {name: process for name, process in listed.items() if process["running"]}

        assert eventually(lambda: {"journal", "sync"} <= set(running()), 30), f"the supervisor runs the journal server and the sync service side by side: {processes(main_socket)}; {logs()}"
        assert all("parent" not in process for process in processes(main_socket).values()), "neither is the other's child"
        journal_post(root, "main", "/journal/messages", {"text": "sent by the sync service"})
        assert eventually(lambda: "sent by the sync service" in texts(), 30), logs()

        first = running()["sync"]
        os.kill(first["pid"], signal.SIGKILL)
        journal_post(root, "main", "/journal/messages", {"text": "made while the sync service was down"})
        assert eventually(lambda: running().get("sync", {}).get("pid") not in (None, first["pid"]), 30), "the supervisor starts a killed sync service again"
        assert running()["sync"]["restarts"] >= 1
        assert eventually(lambda: "made while the sync service was down" in texts(), 30), logs()
        assert texts().count("made while the sync service was down") == 1, "a sync service started again sends what waited, once"

        port, secret = Config(root).stored_port(), (runtime / SECRET_FILE).read_text()
        server_pid, sync_pid = running()["journal"]["pid"], running()["sync"]["pid"]
        lines.clear()
        assert SupervisorSocket.ask(main_socket, {"verb": "restart", "name": "journal", "after": 0}).success
        moved = lambda: Config(root).stored_port() != port and (runtime / SECRET_FILE).read_text() != secret and answering(root)
        assert eventually(lambda: moved() and running()["journal"]["pid"] != server_pid, 60), logs()
        journal_post(root, "main", "/journal/messages", {"text": "sent after the restart"})
        assert eventually(lambda: "sent after the restart" in texts(), 30), logs()
        assert texts().count("sent after the restart") == 1, "and sent once"
        assert running()["sync"]["pid"] == sync_pid, "the sync service runs on through the journal's restart, never started or stopped by the journal"
        assert eventually(lambda: sync_line(root) == "In step with the team", 15) and not [line for line in lines if line.startswith("Not connected")], f"the sync service waits through a restart on a new port with a new secret and reports no team fault: {lines}"
        assert "trying again" not in (runtime / "sync.log").read_text(), (runtime / "sync.log").read_text()[-3000:]

        chat, chat_socket = supervised(root, TEAM_CHAT, home, [])
        started.append(chat)
        assert eventually(lambda: "agent" in processes(chat_socket), 20)
        # the agent's hook script posts its session's start with the launch id its supervisor gave it
        journal_post(root, TEAM_CHAT, "/hooks/claude", {"hook_event_name": "SessionStart", "session_id": "chat1"}, {"X-Journal-Launch": f"test-{TEAM_CHAT}"})
        ask = HttpRequest(f"http://127.0.0.1:{bob.server().port}/journal/messages", data=json.dumps({"text": "please run the tests"}).encode(), method="POST", headers={"Content-Type": "application/json", "X-Journal-Env": TEAM_CHAT})
        asked = json.loads(urlopen(ask, timeout=10).read())
        screen = runtime / "screens" / f"{TEAM_CHAT}.out"
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
        bob_sync.stop()
        bob.runtime().stop()
        server.shutdown()
