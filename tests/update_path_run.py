# Installs fake releases built from this tree with their own install scripts as processes, so it is not in the default run: python3 -m pytest -q tests/update_path_run.py
"""A journal further behind than one update reaches walks the steps of update_steps.json, each installed by its own install.sh so its own code runs its migrations, and a step that fails stops the walk on the last good step, which stays installed and is named in .journal/runtime/update-path.json."""
import json
import os
import shutil
import sqlite3
import subprocess
from pathlib import Path

from journal.support.free_port import FreePort

TREE = Path(__file__).resolve().parents[1]
PARTS = ("src/journal", "src/supervisor", "src/sync_server", "src/sync_service", "src/journal.py", "src/journal.sh", "src/web/dist", "install.sh")
STEPS = {"4.97.0": {"step": True, "oldest": "4.97.0", "reason": "r"}, "4.98.0": {"step": True, "oldest": "4.97.0", "reason": "r"}, "4.99.0": {"step": True, "oldest": "4.98.0", "reason": "r"}}
INSTALL_SECONDS = 300
MIGRATION = """from typing import ClassVar

from journal.db.migration import Migration
from journal.version import VERSION


class StepMark{number}(Migration):
    number: ClassVar[int] = {number}

    def apply(self, connection) -> None:
        connection.execute("CREATE TABLE IF NOT EXISTS step_marks (number INTEGER, version TEXT)")
        connection.execute("INSERT INTO step_marks VALUES (?, ?)", ({number}, VERSION))
"""
BOOTED = """
import json, sys
from pathlib import Path
from journal.app import App
from journal.config import Config
from journal.version import VERSION
App(Config(Path(sys.argv[1]), port=0)).runtime().boot()
print(json.dumps(VERSION))
"""


def git(repo: Path, *words: str) -> str:
    return subprocess.run(["git", "-C", str(repo), "-c", "user.name=t", "-c", "user.email=t@example.com", "-c", "core.hooksPath=/dev/null", *words], capture_output=True, text=True, check=True, timeout=60).stdout


def scratch_repository(repo: Path) -> None:
    for part in PARTS:
        source, copy = TREE / part, repo / part
        copy.parent.mkdir(parents=True, exist_ok=True)
        if source.is_dir():
            shutil.copytree(source, copy, ignore=shutil.ignore_patterns("__pycache__"))
        else:
            shutil.copy2(source, copy)
    (repo / "update_steps.json").write_text(json.dumps(STEPS))
    git(repo, "init", "-q")


def released(repo: Path, version: str, migration: int) -> None:
    (repo / "src" / "journal" / "version.py").write_text(f'VERSION = "{version}"\n')
    if migration:
        (repo / "src" / "journal" / "db" / "migrations" / f"step_mark_{migration}.py").write_text(MIGRATION.format(number=migration))
        with (repo / "src" / "journal" / "db" / "migrations" / "__init__.py").open("a") as registry:
            registry.write(f"\nfrom journal.db.migrations.step_mark_{migration} import StepMark{migration}\nMIGRATIONS = (*MIGRATIONS, StepMark{migration}())\n")
    git(repo, "add", "-A")
    git(repo, "commit", "-q", "-m", f"{version}: a fake release")
    git(repo, "tag", f"v{version}")


def failing_release(repo: Path, version: str) -> None:
    script = repo / "install.sh"
    whole = script.read_text()
    script.write_text("exit 1\n" + whole)
    released(repo, version, 0)
    script.write_text(whole)


def installed(project: Path, home: Path, repo: Path, version: str, port: int) -> subprocess.CompletedProcess:
    script = home / f"install-{version}.sh"
    script.write_text(git(repo, "show", f"v{version}:install.sh"))
    environment = {**os.environ, "HOME": str(home), "AGENT_JOURNAL_REPO": repo.as_uri(), "AGENT_JOURNAL_REF": f"v{version}", "AGENT_JOURNAL_YES": "1", "JOURNAL_PORT": str(port)}
    return subprocess.run(["sh", str(script)], cwd=project, env=environment, capture_output=True, text=True, timeout=INSTALL_SECONDS)


def started_project(tmp_path: Path) -> tuple[Path, Path, Path, int]:
    project, home, repo = tmp_path / "project", tmp_path / "home", tmp_path / "repo"
    for folder in (project, home, repo):
        folder.mkdir()
    git(project, "init", "-q")
    scratch_repository(repo)
    released(repo, "4.97.0", 0)
    return project, home, repo, FreePort.number()


def booted_version(project: Path, home: Path) -> str:
    code = project / ".journal" / "src"
    ran = subprocess.run([(project / ".journal" / "python").read_text().strip(), "-c", BOOTED, str(project)], cwd=code, env={**os.environ, "HOME": str(home), "PYTHONPATH": str(code)}, capture_output=True, text=True, timeout=INSTALL_SECONDS)
    assert ran.returncode == 0, ran.stderr[-2000:]
    return json.loads(ran.stdout.strip().splitlines()[-1])


def test_a_journal_two_steps_behind_is_updated_through_each_step_by_its_own_code(tmp_path: Path):
    project, home, repo, port = started_project(tmp_path)
    released(repo, "4.98.0", 9001)
    released(repo, "4.99.0", 9002)
    assert installed(project, home, repo, "4.97.0", port).returncode == 0
    ran = installed(project, home, repo, "4.99.0", port)
    assert ran.returncode == 0, ran.stderr[-2000:] or ran.stdout[-2000:]
    marks = sqlite3.connect(project / ".journal" / "journal.db").execute("SELECT number, version FROM step_marks ORDER BY number").fetchall()
    assert marks == [(9001, "4.98.0"), (9002, "4.99.0")], "each step's migration ran with that step's own code"
    assert booted_version(project, home) == "4.99.0"
    assert json.loads((project / ".journal" / "runtime" / "update-path.json").read_text()) == {"from": "4.97.0", "to": "4.99.0", "steps": ["4.98.0"], "reached": "4.99.0", "failed": ""}


def test_a_step_that_fails_stops_the_walk_on_the_step_before_it_and_names_it(tmp_path: Path):
    project, home, repo, port = started_project(tmp_path)
    failing_release(repo, "4.98.0")
    released(repo, "4.99.0", 0)
    assert installed(project, home, repo, "4.97.0", port).returncode == 0
    ran = installed(project, home, repo, "4.99.0", port)
    assert ran.returncode != 0 and "the step to 4.98.0 failed" in ran.stderr, ran.stderr[-2000:]
    assert booted_version(project, home) == "4.97.0", "the journal before the failed step stays installed and boots"
    assert json.loads((project / ".journal" / "runtime" / "update-path.json").read_text()) == {"from": "4.97.0", "to": "4.99.0", "steps": ["4.98.0"], "reached": "4.97.0", "failed": "4.98.0"}
