# Runs hooks/environment.sh as a process, so it is not in the default run: python3 -m pytest -q tests/stale_boot_run.py
"""A booting file and a port file naming a dead server's process never hold the next start: it goes ahead without waiting, and both files are cleared."""
import subprocess
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "src" / "journal" / "hooks" / "environment.sh"


def dead_process() -> int:
    finished = subprocess.Popen(["true"])
    finished.wait()
    return finished.pid


def test_a_booting_file_and_port_file_of_a_dead_server_are_cleared_without_waiting(tmp_path: Path):
    runtime = tmp_path / "runtime"
    runtime.mkdir()
    (runtime / "journal.booting").write_text(str(dead_process()))
    (tmp_path / "port").write_text("8421")
    waited = subprocess.run(["sh", "-c", f". {SCRIPT}; journal_boot_wait {tmp_path}"], capture_output=True, text=True, timeout=20).stdout
    assert waited == "0", "the start goes ahead at once"
    assert not (runtime / "journal.booting").exists() and not (tmp_path / "port").exists(), "the stale booting file and port file are gone"
