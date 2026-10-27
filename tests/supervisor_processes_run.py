# Starts real processes, a pty and a unix socket, so it is not in the default run: python3 -m pytest -q tests/supervisor_processes_run.py, before any commit that touches src/supervisor.
"""The supervisor with a real pty and real processes: keys reach the agent, its output comes back, a request lands, and a service is kept alive, restarted less often as it keeps dying, and stopped with every process it started. The agent here is a shell script; no Claude runs."""

import json
import os
import select
import socket
import stat
import time
from pathlib import Path

from supervisor.inbox import Inbox
from supervisor.service import Service
from supervisor.services import Services
from supervisor.supervisor import Supervisor
from supervisor.terminal import Terminal


def pump(supervisor: Supervisor, seconds: float) -> None:
    deadline = time.time() + seconds
    while time.time() < deadline:
        supervisor.relay_once(0.05)
        supervisor.services.revive_stopped()


def ask(supervisor: Supervisor, **request) -> dict:
    """One request to the supervisor's inbox, answered while the loop turns once."""
    with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as link:
        link.connect(str(supervisor.inbox.path))
        link.sendall((json.dumps(request) + "\n").encode())
        supervisor.relay_once(0.2)
        return json.loads(link.makefile("rb").readline())


def test_the_loop_relays_keys_output_and_typed_lines(tmp_path: Path):
    out_r, out_w = os.pipe()
    in_r, in_w = os.pipe()
    terminal = Terminal(["sh", "-c", "while read line; do echo \"got:$line\"; done"], str(tmp_path), {"PATH": os.environ["PATH"]})
    inbox = Inbox(Path(f"/tmp/journal-{os.getuid()}") / f"test-{os.getpid()}.sock", tmp_path / "inboxes" / "main")
    journal = Service("journal", ["sh", "-c", "sleep 30"], tmp_path, {"PATH": os.environ["PATH"]}, tmp_path / "server.log")
    supervisor = Supervisor(terminal, inbox, Services(journal), stdin=in_r, stdout=out_w)
    inbox.open()
    journal.start()
    terminal.start()
    try:
        os.write(in_w, b"hello\r")
        pump(supervisor, 0.5)
        assert ask(supervisor, verb="type", name="agent", line="from the journal") == {"ok": True}
        pump(supervisor, 1.0)
        viewed = os.read(out_r, 65536).decode()
        assert "got:hello" in viewed and "got:from the journal" in viewed
        assert journal.is_active()
        pid = journal._process.pid
        journal._process.terminate()
        journal._process.wait()
        journal._last_start = 0
        pump(supervisor, 0.3)
        assert journal.is_active() and journal._process.pid != pid, "a dead journal is started again"
    finally:
        supervisor.stop()
        journal.stop()
        inbox.close()


def test_a_typed_line_can_wait_before_it_goes_in(tmp_path: Path):
    out_r, out_w = os.pipe()
    in_r, in_w = os.pipe()
    terminal = Terminal(["sh", "-c", "while read line; do echo \"got:$line\"; done"], str(tmp_path), {"PATH": os.environ["PATH"]})
    inbox = Inbox(Path(f"/tmp/journal-{os.getuid()}") / f"test-{os.getpid()}.sock", tmp_path / "inboxes" / "main")
    journal = Service("journal", ["sh", "-c", "sleep 30"], tmp_path, {"PATH": os.environ["PATH"]}, tmp_path / "server.log")
    supervisor = Supervisor(terminal, inbox, Services(journal), stdin=in_r, stdout=out_w)
    inbox.open()
    journal.start()
    terminal.start()
    try:
        ask(supervisor, verb="type", name="agent", line="now")
        ask(supervisor, verb="type", name="agent", line="later", after=0.8)
        pump(supervisor, 0.6)
        viewed = os.read(out_r, 65536).decode()
        assert "got:now" in viewed and "later" not in viewed, "the line with a delay has not gone in yet; lines go in the order they were sent"
        pump(supervisor, 1.0)
        assert "got:later" in os.read(out_r, 65536).decode()
    finally:
        supervisor.stop()
        journal.stop()
        inbox.close()


def test_the_inbox_answers_each_request_and_a_stop_ends_the_supervisor_and_takes_its_inbox_down(tmp_path: Path):
    out_r, out_w = os.pipe()
    terminal = Terminal(["sh", "-c", "trap '' TERM; while true; do sleep 1; done"], str(tmp_path), {"PATH": os.environ["PATH"]})
    inbox = Inbox(Path(f"/tmp/journal-{os.getuid()}") / f"test-{os.getpid()}.sock", tmp_path / "inboxes" / "main")
    journal = Service("journal", ["sh", "-c", "sleep 30"], tmp_path, {"PATH": os.environ["PATH"]}, tmp_path / "server.log")
    supervisor = Supervisor(terminal, inbox, Services(journal), stdin=None, stdout=out_w)
    inbox.open()
    journal.start()
    terminal.start()
    try:
        assert json.loads(inbox.announced_at.read_text()) == {"socket": str(inbox.path), "protocol": 1}
        assert stat.S_IMODE(inbox.path.stat().st_mode) == 0o600 and stat.S_IMODE(inbox.path.parent.stat().st_mode) == 0o700, "only its user can reach the socket"
        assert ask(supervisor, verb="hello") == {"ok": True, "protocol": 1, "verbs": ["hello", "start", "stop", "restart", "list", "keys", "type", "send", "band", "group", "memory"], "outdated": False}
        assert ask(supervisor, verb="band", left="agent-journal", middle="p · main", right="http://127.0.0.1:8420/") == {"ok": True}, "a supervisor with no band takes new words and shows none"
        sleeper = {"verb": "start", "name": "sleeper", "command": ["sh", "-c", "sleep 30"], "folder": str(tmp_path), "log": str(tmp_path / "sleeper.log")}
        assert ask(supervisor, **sleeper) == {"ok": True, "started": True}
        assert ask(supervisor, **sleeper) == {"ok": True, "started": False}, "a name already running is left as it is"
        listed = {p["name"]: p for p in ask(supervisor, verb="list")["processes"]}
        assert listed["agent"]["front"] and listed["agent"]["terminal"] and listed["journal"]["running"] and listed["sleeper"]["running"] and listed["sleeper"]["pid"] > 0
        echo = {"verb": "start", "name": "echo", "command": ["sh", "-c", "read line; echo \"heard:$line\""], "folder": str(tmp_path), "log": str(tmp_path / "echo.log")}
        ask(supervisor, **echo)
        assert ask(supervisor, verb="send", name="echo", data="hello\n") == {"ok": True}
        began = time.time()
        while "heard:hello" not in (tmp_path / "echo.log").read_text() and time.time() - began < 3:
            time.sleep(0.05)
        assert "heard:hello" in (tmp_path / "echo.log").read_text(), "send carries text to a process's input"
        pid = listed["sleeper"]["pid"]
        ask(supervisor, verb="restart", name="sleeper")
        sleeper_pid = lambda: {p["name"]: p for p in ask(supervisor, verb="list")["processes"]}["sleeper"]["pid"]
        began = time.time()
        while sleeper_pid() in (0, pid) and time.time() - began < 5:
            time.sleep(0.05)
        assert sleeper_pid() not in (0, pid), "a restart, done on a thread of its own, starts the service anew"
        assert ask(supervisor, verb="stop", name="sleeper") == {"ok": True}
        assert "sleeper" not in {p["name"] for p in ask(supervisor, verb="list")["processes"]}
        assert ask(supervisor, verb="restart", name="nobody") == {"ok": False, "error": "no process is named 'nobody'"}
        assert ask(supervisor, verb="dance") == {"ok": False, "error": "unknown verb 'dance': hello names the verbs this supervisor takes"}
        assert ask(supervisor, verb="type", name="nobody", line="x") == {"ok": False, "error": "no terminal process is named 'nobody'"}
        assert ask(supervisor, verb="type", line="x") == {"ok": False, "error": "type needs 'name'"}
        assert supervisor._code is None, "a request it cannot carry out is answered and the supervisor stays up"
        ask(supervisor, verb="stop", name="agent")
        began = time.time()
        while supervisor._code is None and time.time() - began < 8:
            supervisor.relay_once(0.05)
        assert supervisor._code is not None, "an agent that ignores TERM is still ended"
        assert terminal.exited() is None, "reaped once, never asked after again"
    finally:
        journal.stop()
        inbox.close()
    assert not inbox.announced_at.exists()


def test_a_typed_lines_enter_waits_until_the_line_has_gone_in(tmp_path: Path):
    from supervisor import terminal as terminal_module
    read_end, write_end = os.pipe()
    terminal = Terminal(["sh"], str(tmp_path), {})
    terminal.fd = write_end
    os.set_blocking(write_end, False)
    filled = 0
    while True:
        try:
            filled += os.write(write_end, b"x" * 65536)
        except BlockingIOError:
            break
    terminal.write(b"k")
    terminal.type("from the journal")
    terminal.pump()
    terminal.feed()
    time.sleep(terminal_module.ENTER_DELAY_SECONDS + 0.1)
    terminal.pump()
    assert terminal._enter_due == 0.0 and not any(segment == b"\r" for segment, _ in terminal._pieces), "the line has not gone in: no Enter yet"
    os.read(read_end, filled)
    terminal.feed()
    terminal.feed()
    assert os.read(read_end, 1024) == b"kfrom the journal", "the key and the line, each in a write of its own, and no Enter in the same piece"
    terminal.pump()
    assert not terminal.has_pending, "the Enter waits a moment after the line is in"
    time.sleep(terminal_module.ENTER_DELAY_SECONDS + 0.1)
    terminal.pump()
    terminal.feed()
    assert os.read(read_end, 1024) == b"\r"
    os.close(read_end)
    os.close(write_end)


def test_a_service_that_keeps_dying_is_started_again_less_often_and_never_left_down(tmp_path: Path, monkeypatch):
    import supervisor.service as service
    monkeypatch.setattr(service, "BACKOFF", 0.05)
    monkeypatch.setattr(service, "LONGEST_WAIT_SECONDS", 0.2)
    crashing = Service("crashing", ["sh", "-c", "exit 1"], tmp_path, {"PATH": os.environ["PATH"]}, tmp_path / "crash.log")
    crashing.start()
    began = time.time()
    while crashing.described()["restarts"] < 8 and time.time() - began < 5:
        crashing.revive()
        time.sleep(0.02)
    assert crashing.described()["restarts"] >= 8, "a kept service is started again however often it dies"
    once = Service("once", ["true"], tmp_path, {}, tmp_path / "once.log", persistent=False)
    once.start()
    time.sleep(0.2)
    once.revive()
    assert once.described()["restarts"] == 0, "a process not kept is left down when it ends"


def test_stopping_a_service_ends_every_process_it_started(tmp_path: Path):
    family = Service("family", ["sh", "-c", "sleep 30 & sleep 30"], tmp_path, {"PATH": os.environ["PATH"]}, tmp_path / "family.log")
    family.start()
    time.sleep(0.2)
    group = family._process.pid
    family.stop()
    try:
        os.killpg(group, 0)
        responsive = True
    except ProcessLookupError:
        responsive = False
    assert not responsive, "the child it left in the background went with it"


def test_a_restart_replaces_only_the_resume_and_keeps_the_rest_of_the_command(tmp_path: Path):
    terminal = Terminal(["env", "KEPT=yes", "sh", "-c", "echo seen:$KEPT:$RESUMED; sleep 5"], str(tmp_path), {"PATH": os.environ["PATH"]}, ("RESUMED=first",))

    def output(deadline: bytes) -> bytes:
        viewed, began = b"", time.time()
        while deadline not in viewed and time.time() - began < 3:
            viewed += terminal.read() if select.select([terminal.fd], [], [], 0.1)[0] else b""
        return viewed

    terminal.start()
    assert b"seen:yes:first" in output(b"seen:")
    terminal.restart(("RESUMED=second",))
    viewed = output(b"seen:")
    terminal.stop(1.0)
    assert b"seen:yes:second" in viewed, "the restart put its own resume after the program and kept the rest of the command"


def test_an_agent_that_dies_is_started_again_and_one_that_quits_ends_the_supervisor(tmp_path: Path):
    marker = tmp_path / "died once"
    terminal = Terminal(["sh", "-c", f'test -f "{marker}" || {{ touch "{marker}"; exit 1; }}; sleep 60'], str(tmp_path), {"PATH": os.environ["PATH"]})
    inbox = Inbox(Path(f"/tmp/journal-{os.getuid()}") / f"revive-{os.getpid()}.sock", tmp_path / "inboxes" / "main")
    journal = Service("journal", ["sh", "-c", "sleep 60"], tmp_path, {"PATH": os.environ["PATH"]}, tmp_path / "server.log")
    keys, _ = os.pipe()
    supervisor = Supervisor(terminal, inbox, Services(journal), stdin=keys, stdout=os.open(os.devnull, os.O_WRONLY))
    inbox.open()
    journal.start()
    terminal.start()
    try:
        deadline = time.time() + 3
        while time.time() < deadline and not (marker.exists() and terminal.pid > 0 and supervisor._revivals):
            supervisor.relay_once(0.05)
        pump(supervisor, 0.5)
        front = supervisor.described()[0]
        assert supervisor._code is None and front["running"] and front["restarts"] == 1 and journal.is_active(), "the agent died, was started again, and the journal kept running"
    finally:
        supervisor.stop()
        supervisor.services.stop_all()
        inbox.close()
    quitting = Terminal(["sh", "-c", "exit 0"], str(tmp_path), {"PATH": os.environ["PATH"]})
    quits = Supervisor(quitting, Inbox(Path(f"/tmp/journal-{os.getuid()}") / f"quit-{os.getpid()}.sock", tmp_path / "inboxes" / "other"), Services(Service("journal", ["sh", "-c", "sleep 60"], tmp_path, {"PATH": os.environ["PATH"]}, tmp_path / "s.log")), stdin=keys, stdout=os.open(os.devnull, os.O_WRONLY))
    quits.inbox.open()
    quitting.start()
    try:
        deadline = time.time() + 3
        while time.time() < deadline and quits._code is None:
            quits.relay_once(0.05)
        assert quits._code == 0, "a clean exit ends the supervisor"
    finally:
        quits.inbox.close()


def test_the_launcher_starts_the_supervisor_again_whenever_it_exits_and_exits_when_it_exits_0(tmp_path: Path):
    import subprocess
    runs = tmp_path / "runs"
    python = tmp_path / "python"
    python.write_text(f'#!/bin/sh\necho "$3" >> "{runs}"\ncount=$(wc -l < "{runs}")\n[ "$count" -eq 1 ] && exit 75\n[ "$count" -eq 2 ] && exit 1\nexit 0\n')
    python.chmod(0o755)
    script = Path(__file__).parent.parent / "src" / "supervisor" / "launcher.sh"
    finished = subprocess.run(["sh", str(script), str(python), "launch.json"], cwd=tmp_path, timeout=10)
    assert finished.returncode == 0 and runs.read_text().split() == ["launch.json"] * 3, "a restart and a fault each start it again; its exit with 0 ends the loop"
    assert len(script.read_text().splitlines()) <= 10


def test_two_restarts_of_one_service_at_once_take_turns_and_raise_nothing(tmp_path: Path):
    import threading

    journal = Service("journal", ["sh", "-c", "sleep 30"], tmp_path, {"PATH": os.environ["PATH"]}, tmp_path / "server.log")
    journal.start()
    faults = []

    def restarted():
        try:
            journal.restart()
        except Exception as fault:
            faults.append(fault)

    threads = [threading.Thread(target=restarted) for _ in range(2)]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join(timeout=20)
    try:
        assert faults == [] and journal.is_active(), "the second restart waits for the first, and the service ends up running"
    finally:
        journal.stop()


def test_a_revive_while_a_restart_runs_leaves_one_process_running(tmp_path: Path):
    import threading

    pids = tmp_path / "pids"
    journal = Service("journal", ["sh", "-c", f"echo $$ >> {pids}; trap 'sleep 0.3; exit 0' TERM; while true; do sleep 0.05; done"], tmp_path, {"PATH": os.environ["PATH"]}, tmp_path / "server.log")
    journal.start()
    time.sleep(0.3)
    restart = threading.Thread(target=journal.restart)
    restart.start()
    while restart.is_alive():
        journal.revive()
    time.sleep(0.3)
    try:
        started = [int(line) for line in pids.read_text().split()]
        running = [pid for pid in started if os.system(f"kill -0 {pid} 2>/dev/null") == 0]
        assert running == [journal.described()["pid"]], "the restart's own process is the only one left running"
    finally:
        journal.stop()


def test_a_supervisor_and_a_chain_shell_end_within_ten_seconds_of_their_owner_killed(tmp_path: Path, monkeypatch):
    import signal
    import subprocess
    import sys

    from journal.features.shell.support.chain_worker import SHELL_SETUP
    import supervisor.supervisor as supervising

    monkeypatch.setattr(supervising, "OWNER_CHECK_SECONDS", 0.5)
    owner = subprocess.Popen([sys.executable, "-c", "import time; time.sleep(60)"])
    terminal = Terminal(["sh", "-c", "sleep 60"], str(tmp_path), {"PATH": os.environ["PATH"]})
    inbox = Inbox(Path(f"/tmp/journal-{os.getuid()}") / f"owner-{os.getpid()}.sock", tmp_path / "inboxes" / "main")
    keys, _ = os.pipe()
    supervisor = Supervisor(terminal, inbox, Services(), stdin=keys, stdout=os.open(os.devnull, os.O_WRONLY), owner=owner.pid)
    shell = subprocess.Popen(["sh"], stdin=subprocess.PIPE, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, start_new_session=True)
    shell.stdin.write((SHELL_SETUP.replace("__JOURNAL_OWNER", str(owner.pid)) + "sleep 120\n").encode())
    shell.stdin.flush()
    inbox.open()
    terminal.start()
    try:
        pump(supervisor, 1.0)
        assert supervisor._code is None and shell.poll() is None, "both run while their owner lives"
        owner.send_signal(signal.SIGKILL)
        owner.wait()
        deadline = time.time() + 10
        while time.time() < deadline and (supervisor._code is None or shell.poll() is None):
            supervisor.turn()
        assert supervisor._code == 0, "the supervisor ends once the command that launched it is gone"
        assert shell.poll() is not None, "the chain shell and the command it runs end once the server that started it is gone"
        try:
            os.killpg(shell.pid, 0)
            group_left = True
        except ProcessLookupError:
            group_left = False
        assert not group_left, "nothing of its process group is left"
    finally:
        supervisor.stop()
        inbox.close()
        if shell.poll() is None:
            os.killpg(shell.pid, signal.SIGKILL)


def test_a_service_that_fails_its_health_url_or_lets_its_health_file_go_stale_is_started_again_and_why_is_logged(tmp_path: Path):
    import threading
    from http.server import BaseHTTPRequestHandler, HTTPServer
    from supervisor.health_check import HealthCheck

    class Unwell(BaseHTTPRequestHandler):
        def do_GET(self):
            self.send_response(503)
            self.end_headers()

        def log_message(self, *args):
            return

    stand_in = HTTPServer(("127.0.0.1", 0), Unwell)
    threading.Thread(target=stand_in.serve_forever, daemon=True).start()
    environ = {"PATH": os.environ["PATH"]}
    web = Service("web", ["sleep", "30"], tmp_path, environ, tmp_path / "web.log", health=HealthCheck(url=f"http://127.0.0.1:{stand_in.server_address[1]}/health", grace_seconds=0, interval_seconds=0, timeout_seconds=1, failures=2))
    beat = Service("beat", ["sleep", "30"], tmp_path, environ, tmp_path / "beat.log", health=HealthCheck(file=str(tmp_path / "beat.fresh"), max_age_seconds=1, grace_seconds=0, interval_seconds=0, failures=1))
    faults = tmp_path / "supervisor.log"
    supervisor = Supervisor(Terminal(["true"], str(tmp_path), environ), Inbox(tmp_path / "s.sock", tmp_path / "announce"), Services(web, beat), stdin=None, faults=faults)
    web.start(), beat.start()
    web_pid, beat_pid = web.described()["pid"], beat.described()["pid"]
    watching = threading.Thread(target=supervisor.watched_health, daemon=True)
    watching.start()
    try:
        deadline = time.monotonic() + 10
        while time.monotonic() < deadline and (web.described()["pid"] in (0, web_pid) or beat.described()["pid"] in (0, beat_pid)):
            time.sleep(0.1)
        assert web.described()["pid"] not in (0, web_pid) and web.described()["restarts"] >= 1, "a service whose health URL keeps answering unwell is started again"
        assert beat.described()["pid"] not in (0, beat_pid), "and so is one whose health file was never written"
        logged = faults.read_text()
        assert "web failed its health check 2 times in a row" in logged and "answered 503" in logged and "beat failed its health check 1 times in a row" in logged, logged
    finally:
        supervisor._code = 0
        watching.join(5)
        web.stop(), beat.stop()
        stand_in.shutdown()


def test_an_agent_whose_terminal_moves_while_its_hooks_file_stands_still_is_warned_once_until_the_file_moves(tmp_path: Path, monkeypatch):
    import supervisor.supervisor as supervisor_module
    from supervisor.front_health import FrontHealth
    monkeypatch.setattr(supervisor_module, "FRONT_CHECK_SECONDS", 0.2)
    out_r, out_w = os.pipe()
    in_r, _ = os.pipe()
    hooks = tmp_path / "hooks" / "main.fired"
    terminal = Terminal(["sh", "-c", "while true; do echo tick; sleep 0.2; done"], str(tmp_path), {"PATH": os.environ["PATH"]})
    inbox = Inbox(Path(f"/tmp/journal-{os.getuid()}") / f"test-{os.getpid()}-front.sock", tmp_path / "inboxes" / "main")
    supervisor = Supervisor(terminal, inbox, Services(), stdin=in_r, stdout=out_w, front_health=FrontHealth(str(hooks), 1.0, "WARNED-DEAD-HOOKS", 5.0))
    inbox.open()
    terminal.start()
    shown = bytearray()

    def run(seconds: float) -> str:
        deadline = time.time() + seconds
        while time.time() < deadline:
            supervisor.turn()
            while select.select([out_r], [], [], 0)[0]:
                shown.extend(os.read(out_r, 65536))
        return shown.decode(errors="replace")

    try:
        assert run(4).count("WARNED-DEAD-HOOKS") == 1, "an agent whose output keeps moving while its hooks file stands still past the limit is warned, once"
        assert run(2).count("WARNED-DEAD-HOOKS") == 1, "and not again while the episode lasts"
        hooks.parent.mkdir(parents=True)
        hooks.write_text("1")
        run(0.5)
        assert run(3).count("WARNED-DEAD-HOOKS") == 2, "a hook written ends the episode, and the next one is warned again"
    finally:
        supervisor.stop()
        inbox.close()


def test_a_boot_that_never_answers_booted_is_started_again_once_then_from_the_last_good_copy_and_a_good_boot_keeps_its_code(tmp_path: Path):
    import threading
    from http.server import BaseHTTPRequestHandler, HTTPServer
    from supervisor.boot_watch import BootWatch
    from supervisor.health_check import HealthCheck

    answer = {"status": 503, "body": b"{}"}

    class Standing(BaseHTTPRequestHandler):
        def do_GET(self):
            self.send_response(answer["status"])
            self.end_headers()
            self.wfile.write(answer["body"])

        def log_message(self, *args):
            return

    stand_in = HTTPServer(("127.0.0.1", 0), Standing)
    threading.Thread(target=stand_in.serve_forever, daemon=True).start()
    source, kept = tmp_path / "package", tmp_path / "last_good"
    source.mkdir(), kept.mkdir()
    (source / "version").write_text("broken"), (kept / "version").write_text("good")
    notice = tmp_path / "notice.txt"
    log = tmp_path / "web.log"
    log.write_text("Traceback (most recent call last):\n  File seed.py\nValueError: a removed reader\n")
    watch = BootWatch(notice=str(notice), keep_source=str(source), keep_copy=str(kept), fallback_command=["sleep", "31"], seconds=0)
    health = HealthCheck(url=f"http://127.0.0.1:{stand_in.server_address[1]}/health", grace_seconds=0, interval_seconds=0, timeout_seconds=1, failures=99)
    web = Service("web", ["sleep", "30"], tmp_path, {"PATH": os.environ["PATH"]}, log, health=health, boot=watch)
    web.start()
    try:
        assert "did not boot in time" in web.health_restart() and "a removed reader" in notice.read_text(), "the first failed boot starts it again and says what failed"
        assert "started from the last version that booted" in web.health_restart() and web.command == ["sleep", "31"], "the second starts the copy kept at the last good boot"
        assert notice.read_text().count("\n") == 2 and (kept / "version").read_text() == "good", "both are told in the notice and the good copy is untouched while it runs"
        answer.update(status=200, body=b'{"phase": "booted"}')
        fresh = Service("web", ["sleep", "30"], tmp_path, {"PATH": os.environ["PATH"]}, log, health=health, boot=watch)
        fresh.start()
        fresh.health_restart()
        assert (kept / "version").read_text() == "broken", "a boot that answers booted keeps its code as the last good one"
        fresh.stop()
    finally:
        web.stop()
        stand_in.shutdown()


def test_a_worker_group_handed_to_the_supervisor_is_ended_when_the_supervisor_exits(tmp_path: Path):
    import signal
    import subprocess
    from types import SimpleNamespace
    from supervisor.request import Request
    from supervisor.verbs import Verbs
    services = Services()
    worker = subprocess.Popen(["sh", "-c", "sleep 60 & wait"], start_new_session=True)
    reply = Verbs(SimpleNamespace(services=services)).handle(Request.parsed({"verb": "group", "pid": worker.pid}))
    assert reply.is_success, reply
    services.stop_all()
    assert worker.wait(timeout=10) == -signal.SIGTERM, "the worker's process group ends as the supervisor exits"


def test_the_supervisor_reads_the_resident_memory_of_a_handed_process_tree(tmp_path: Path):
    import subprocess
    from types import SimpleNamespace
    from supervisor.request import Request
    from supervisor.verbs import Verbs
    services = Services()
    tree = subprocess.Popen(["sh", "-c", "sleep 60 & sleep 60 & wait"], start_new_session=True)
    try:
        time.sleep(0.5)
        services.group(tree.pid)
        reply = Verbs(SimpleNamespace(services=services)).handle(Request.parsed({"verb": "memory"}))
        assert reply.is_success and reply.answer["groups"][str(tree.pid)] > 0, reply
    finally:
        services.stop_all()
        tree.wait(timeout=10)

