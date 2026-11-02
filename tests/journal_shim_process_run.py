# Runs the journal shim as a process for server and terminal cases, so it is not in the default run: python3 -m pytest -q tests/journal_shim_process_run.py
"""The journal command lets the package run a command itself only when no server could be reached, never after a server took it."""
import os
import shutil
import socket
import subprocess
import threading
from pathlib import Path

import pytest

from tests.test_cli import MAIN, app

SOURCE = Path(__file__).resolve().parent.parent / "src"


def shim_copy(root: Path) -> Path:
    (root / "src" / "journal" / "hooks").mkdir(parents=True)
    shutil.copy(SOURCE / "journal.sh", root / "src" / "journal.sh")
    shutil.copy(SOURCE / "journal" / "hooks" / "environment.sh", root / "src" / "journal" / "hooks" / "environment.sh")
    (root / "src" / "journal.py").write_text("from pathlib import Path\nPath('ran-here').write_text('yes')\n")
    (root / ".journal").mkdir()
    return root / "src" / "journal.sh"


def broken_off_server() -> int:
    listener = socket.socket()
    listener.bind(("127.0.0.1", 0))
    listener.listen()
    def taken() -> None:
        connection, _ = listener.accept()
        connection.recv(65536)
        connection.close()
    threading.Thread(target=taken, daemon=True).start()
    return listener.getsockname()[1]


def shim_run(shim: Path, root: Path) -> subprocess.CompletedProcess:
    return subprocess.run(["sh", str(shim), "task", "list"], cwd=root, env={"PATH": "/usr/bin:/bin", "JOURNAL_ROOT": str(root), "JOURNAL_ENV": "main"}, capture_output=True, text=True, timeout=20)


def test_a_command_the_server_took_and_broke_off_on_is_not_run_a_second_time_by_the_package(tmp_path: Path):
    shim = shim_copy(tmp_path)
    (tmp_path / ".journal" / "port").write_text(str(broken_off_server()))
    ran = shim_run(shim, tmp_path)
    assert ran.returncode == 1 and "was not run a second time" in ran.stderr, ran.stderr
    assert not (tmp_path / "ran-here").exists(), "the package never runs a command the server may still be running"


def test_a_command_no_server_could_take_is_run_by_the_package(tmp_path: Path):
    shim = shim_copy(tmp_path)
    closed = socket.socket()
    closed.bind(("127.0.0.1", 0))
    (tmp_path / ".journal" / "port").write_text(str(closed.getsockname()[1]))
    closed.close()
    ran = shim_run(shim, tmp_path)
    assert (tmp_path / "ran-here").read_text() == "yes", ran.stderr


def slow_server() -> int:
    listener = socket.socket()
    listener.bind(("127.0.0.1", 0))
    listener.listen()
    def answered() -> None:
        connection, _ = listener.accept()
        connection.recv(65536)
        connection.sendall(b"HTTP/1.1 200 OK\r\nContent-Type: text/plain\r\nConnection: close\r\n\r\nstep 1/5: asking the plugins\n")
        threading.Event().wait(3)
        connection.sendall(b"__journal_exit 0\n")
        connection.close()
    threading.Thread(target=answered, daemon=True).start()
    return listener.getsockname()[1]


def test_a_line_the_server_streams_reaches_the_shims_output_before_the_command_ends(tmp_path: Path):
    import time
    shim = shim_copy(tmp_path)
    (tmp_path / ".journal" / "port").write_text(str(slow_server()))
    began = time.monotonic()
    process = subprocess.Popen(["sh", str(shim), "worker", "merge", "1"], cwd=tmp_path, env={"PATH": "/usr/bin:/bin", "JOURNAL_ROOT": str(tmp_path), "JOURNAL_ENV": "main"}, stdout=subprocess.PIPE, text=True)
    first = process.stdout.readline()
    arrived = time.monotonic() - began
    process.wait(timeout=10)
    assert first.startswith("step 1/5") and arrived < 2, f"the step arrived after {arrived:.1f} s"


def test_a_workers_shim_never_runs_the_package_when_no_server_answers(app):
    environ = {key: value for key, value in os.environ.items() if key != "JOURNAL_SESSION"}
    environ.update(JOURNAL_ROOT=str(app.config.root), JOURNAL_ENV="main", JOURNAL_ACTOR="worker:1", JOURNAL_ACTOR_TOKEN="tok")
    (app.config.home / "port").unlink(missing_ok=True)
    outcome = subprocess.run(["sh", str(SOURCE / "journal.sh"), "task", "list"], env=environ, capture_output=True, text=True, timeout=10)
    assert outcome.returncode == 1 and "restarting" in outcome.stderr, "a worker's command waits for the server that can check its token"


@pytest.mark.parametrize("online", [False, True])
def test_the_shim_attributes_a_codex_command_with_and_without_a_server(app, online):
    from journal.models.agent import Agent
    from journal.providers.claude import Claude
    from journal.repositories.agents import Agents
    from journal.repositories.environments import Environments
    from journal.repositories.scope import Scope
    from journal.support.actor import Actor

    agents = app.container.get(Agents)
    development = app.container.get(Environments).lookup("development")
    with app.container.get(Scope).environment(development.id):
        agents.save(Agent(session="codex-session", environment_id=development.id, provider="codex", is_overview_read=False), Actor.system())
    environ = {key: value for key, value in os.environ.items() if key not in ("JOURNAL_SESSION", "CODEX_SANDBOX", *Claude.inherited_markers)}
    environ.update(JOURNAL_ROOT=str(app.config.root), JOURNAL_ENV="development", JOURNAL_PORT="0", CODEX_THREAD_ID="codex-session", CODEX_CI="1")
    server = app.server()
    if online:
        server.start()
    try:
        outcome = subprocess.run(["sh", str(SOURCE / "journal.sh"), "environment", "overview"], env=environ, capture_output=True, text=True, timeout=10)
        assert outcome.returncode == 0, outcome.stderr
        with app.container.get(Scope).environment(development.id):
            assert agents.session_agent("codex-session").is_overview_read
    finally:
        server.stop()


def test_a_command_the_server_fails_on_prints_the_fault_and_exits_non_zero(app, tmp_path):
    from journal.providers.claude import Claude

    environ = {key: value for key, value in os.environ.items() if key not in ("JOURNAL_SESSION", "CODEX_SANDBOX", *Claude.inherited_markers)}
    environ.update(JOURNAL_ROOT=str(app.config.root), JOURNAL_ENV="main", JOURNAL_PORT="0")
    server = app.server()
    server.start()
    try:
        missing = tmp_path / "gone.md"
        outcome = subprocess.run(["sh", str(SOURCE / "journal.sh"), "doc", "create", "Notes", "--abstract", "The notes", "--file", str(missing)], env=environ, capture_output=True, text=True, timeout=10)
        assert outcome.returncode == 1 and "gone.md" in outcome.stderr, "a fault is printed with what it names, never a silent success"
    finally:
        server.stop()


def test_the_shim_runs_an_aliases_line_typed_at_a_terminal(app):
    assert app.console().run(["alias", "add", "hello", "echo hi from"], MAIN).code == 0
    server = app.server()
    server.start()
    try:
        environ = {**os.environ, "JOURNAL_ROOT": str(app.config.root), "JOURNAL_ENV": "main"}
        (app.config.home / "port").write_text(str(server.port))
        typed = subprocess.run(["sh", str(SOURCE / "journal.sh"), "hello", "the terminal"], env=environ, capture_output=True, text=True, timeout=10)
        assert typed.returncode == 0 and typed.stdout == "hi from the terminal\n", typed.stdout + typed.stderr
    finally:
        server.stop()
