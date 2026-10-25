# Runs hooks/hook.sh as a process against a stand-in server, so it is not in the default run: python3 -m pytest -q tests/hook_script_run.py
"""The hook script prints a refusal that carries the agent's own answer as it is, with exit 0, and any other refusal to stderr with exit 2."""
import json
import os
import subprocess
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "src" / "journal" / "hooks" / "hook.sh"


def answering(body: dict) -> HTTPServer:
    class Handler(BaseHTTPRequestHandler):
        def do_POST(self):
            self.rfile.read(int(self.headers["Content-Length"]))
            raw = json.dumps(body).encode()
            self.send_response(409)
            self.send_header("Content-Length", str(len(raw)))
            self.end_headers()
            self.wfile.write(raw)

        def log_message(self, *args):
            pass

    server = HTTPServer(("127.0.0.1", 0), Handler)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    return server


def hooked(tmp_path: Path, body: dict) -> subprocess.CompletedProcess:
    server = answering(body)
    (tmp_path / ".journal").mkdir(exist_ok=True)
    (tmp_path / ".journal" / "port").write_text(str(server.server_port))
    sent = json.dumps({"hook_event_name": "PreToolUse", "session_id": "s1", "tool_name": "Bash", "tool_input": {"command": "cd /tmp"}})
    try:
        return subprocess.run(["sh", str(SCRIPT), "claude", str(tmp_path)], input=sent, capture_output=True, text=True, env={**os.environ, "AGENT_JOURNAL_ACTIVE": "1", "JOURNAL_ACTOR": "agent"}, timeout=30)
    finally:
        server.shutdown()


def test_a_refusal_with_the_agents_own_answer_is_printed_as_it_is_and_exits_zero(tmp_path: Path):
    answer = {"hookSpecificOutput": {"hookEventName": "PreToolUse", "permissionDecision": "deny", "permissionDecisionReason": "cd would move your shell, \"quoted\", a, \"error\": in it"}}
    ran = hooked(tmp_path, {"answer": answer, "error": "cd would move your shell"})
    assert ran.returncode == 0 and json.loads(ran.stdout) == answer and ran.stderr == "", (ran.stdout, ran.stderr)


def test_a_refusal_without_an_answer_goes_to_stderr_with_exit_two(tmp_path: Path):
    ran = hooked(tmp_path, {"error": "a plain refusal"})
    assert ran.returncode == 2 and "a plain refusal" in ran.stderr


def test_the_hook_script_writes_the_time_of_every_hook_it_sends_whether_or_not_the_server_takes_it(tmp_path: Path):
    import time
    sent = json.dumps({"hook_event_name": "PreToolUse", "session_id": "s1", "tool_name": "Bash", "tool_input": {"command": "ls"}})
    environ = {**os.environ, "AGENT_JOURNAL_ACTIVE": "1", "JOURNAL_ACTOR": "agent", "JOURNAL_ENV": "spike"}
    (tmp_path / ".journal").mkdir()
    (tmp_path / ".journal" / "port").write_text("9")
    before = int(time.time())
    subprocess.run(["sh", str(SCRIPT), "claude", str(tmp_path)], input=sent, capture_output=True, text=True, env=environ, timeout=30)
    fired = tmp_path / ".journal" / "runtime" / "hooks" / "spike.fired"
    assert fired.is_file() and before <= int(fired.read_text()) <= int(time.time()), "a hook the server never took, with nothing listening on its port, is still written down with its time, under its environment's name"


def test_a_journal_that_takes_the_hook_and_never_answers_is_gone_around_within_seconds(tmp_path: Path):
    import socket
    import time
    silent = socket.socket()
    silent.bind(("127.0.0.1", 0))
    silent.listen(8)
    (tmp_path / ".journal" / "runtime").mkdir(parents=True)
    (tmp_path / ".journal" / "port").write_text(str(silent.getsockname()[1]))
    sent = json.dumps({"hook_event_name": "PreToolUse", "session_id": "s1", "tool_name": "Bash", "tool_input": {"command": "ls"}})
    began = time.monotonic()
    ran = subprocess.run(["sh", str(SCRIPT), "claude", str(tmp_path)], input=sent, capture_output=True, text=True, env={**os.environ, "AGENT_JOURNAL_ACTIVE": "1", "JOURNAL_ACTOR": "agent"}, timeout=30)
    silent.close()
    assert ran.returncode == 0 and ran.stdout == "" and time.monotonic() - began < 5, (ran.returncode, ran.stdout, time.monotonic() - began)
    assert " hook claude" in (tmp_path / ".journal" / "runtime" / "bypass.log").read_text(), "the miss is noted for the journal to say"
