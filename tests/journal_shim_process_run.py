# Runs the journal shim as a process against a server that breaks off, so it is not in the default run: python3 -m pytest -q tests/journal_shim_process_run.py
"""The journal command lets the package run a command itself only when no server could be reached, never after a server took it."""
import shutil
import socket
import subprocess
import threading
from pathlib import Path

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
