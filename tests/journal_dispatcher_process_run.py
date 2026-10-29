# Runs the journal command at ~/.local/bin as a shell process, so it is not in the default run: python3 -m pytest -q tests/journal_dispatcher_process_run.py
"""The journal command outside a project finds the project from JOURNAL_ROOT when set, else from the folder it runs in."""
import os
import subprocess
from pathlib import Path

from journal.launcher.dispatcher import Dispatcher


def project(root: Path) -> Path:
    (root / ".journal" / "src").mkdir(parents=True)
    (root / ".journal" / "src" / "journal.sh").write_text('echo "journal of $JOURNAL_ROOT: $*"\n')
    return root


def journal(home: Path, folder: Path, **environment: str) -> subprocess.CompletedProcess:
    (home / ".local" / "bin").mkdir(parents=True, exist_ok=True)
    command = Dispatcher(home).write()
    variables = {key: value for key, value in os.environ.items() if key != "JOURNAL_ROOT"}
    return subprocess.run([str(command), "task", "list"], cwd=folder, env={**variables, **environment}, capture_output=True, text=True, timeout=10)


def test_the_journal_command_run_outside_the_project_reaches_the_project_journal_root_names(tmp_path: Path):
    shop, seat = project(tmp_path / "shop"), tmp_path / "seat"
    seat.mkdir()
    reached = journal(tmp_path / "home", seat, JOURNAL_ROOT=str(shop))
    assert reached.returncode == 0 and reached.stdout.strip() == f"journal of {shop}: task list", "JOURNAL_ROOT names the project when the folder is outside it"
    lost = journal(tmp_path / "home", seat)
    assert lost.returncode == 1 and "no .journal/ here or above" in lost.stderr, "without it a folder outside every project reaches no journal"
    inside = journal(tmp_path / "home", project(tmp_path / "other") / ".journal")
    assert inside.stdout.strip() == f"journal of {tmp_path / 'other'}: task list", "and inside a project the walk up from the folder finds it as before"
