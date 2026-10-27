# Installs released versions with their own install scripts and runs them as processes, so it is not in the default run: python3 -m pytest -q tests/update_matrix_run.py
"""Every release from 4.60.0 on, installed into a project of its own and given rows the way an agent and the user write them, updates to every later release and to this tree through the update's own install script, and the updated journal boots and reads every row the older one wrote."""
import json
import os
import subprocess
from pathlib import Path

import pytest

REPOSITORY = Path(__file__).resolve().parents[1]
FIRST_RELEASE = (4, 60, 0)
TREE = "tree"
STEP_SECONDS = 300
SCRATCH_PORT = "8531"

SEED = """
import json, sys
from pathlib import Path
from journal.app import App
from journal.config import Config
from journal.support.caller import Caller
app = App(Config(Path(sys.argv[1]), port=0))
app.runtime().boot()
version = sys.argv[2]
agent, user = Caller.agent("main", "s1", "claude"), Caller.user("main")
writes = ((["task", "create", f"written on {version}", "--brief", "b"], agent), (["message", "send", f"said on {version}"], user), (["plan", "create", f"planned on {version}", "--brief", "b"], agent))
codes = [app.console().run(argv, caller).code for argv, caller in writes]
print(json.dumps(codes))
"""

READ = """
import json, sys
from pathlib import Path
from journal.app import App
from journal.config import Config
from journal.support.caller import Caller
app = App(Config(Path(sys.argv[1]), port=0))
app.runtime().boot()
user = Caller.user("main")
print(json.dumps({noun: app.console().run([noun, "list"], user).text for noun in ("task", "message", "plan")}))
"""


def releases() -> list[str]:
    tags = subprocess.run(["git", "tag", "--list", "v4.*"], cwd=REPOSITORY, capture_output=True, text=True, timeout=30, check=True).stdout.split()
    numbered = sorted((tuple(int(n) for n in tag[1:].split(".")), tag) for tag in tags)
    return [tag for number, tag in numbered if number >= FIRST_RELEASE]


def pairs() -> list[tuple[str, str]]:
    versions = [*releases(), TREE]
    return [(start, target) for at, start in enumerate(versions[:-1]) for target in versions[at + 1:]]


def environment(home: Path, ref: str) -> dict[str, str]:
    return {**os.environ, "HOME": str(home), "AGENT_JOURNAL_REPO": REPOSITORY.as_uri(), "AGENT_JOURNAL_REF": ref, "AGENT_JOURNAL_YES": "1", "JOURNAL_PORT": SCRATCH_PORT}


def installed(project: Path, home: Path, version: str) -> None:
    if version == TREE:
        script, ref = REPOSITORY / "install.sh", "development"
    else:
        script, ref = home / f"install-{version}.sh", version
        script.write_text(subprocess.run(["git", "show", f"{version}:install.sh"], cwd=REPOSITORY, capture_output=True, text=True, timeout=30, check=True).stdout)
    ran = subprocess.run(["sh", str(script)], cwd=project, env=environment(home, ref), capture_output=True, text=True, timeout=STEP_SECONDS)
    assert ran.returncode == 0, f"the install of {version} failed: {ran.stderr[-2000:] or ran.stdout[-2000:]}"


def journal_ran(project: Path, home: Path, script: str, *values: str) -> str:
    code = project / ".journal" / "src"
    ran = subprocess.run([str((project / ".journal" / "python").read_text().strip()), "-c", script, str(project), *values], cwd=code, env={**environment(home, ""), "PYTHONPATH": str(code)}, capture_output=True, text=True, timeout=STEP_SECONDS)
    assert ran.returncode == 0, ran.stderr[-2000:]
    return ran.stdout.strip().splitlines()[-1]


@pytest.mark.parametrize(("start", "target"), pairs())
def test_a_release_updates_to_a_later_one_and_reads_every_row_it_wrote(tmp_path: Path, start: str, target: str):
    project, home = tmp_path / "project", tmp_path / "home"
    project.mkdir()
    home.mkdir()
    subprocess.run(["git", "init", "-q"], cwd=project, timeout=30, check=True)
    installed(project, home, start)
    assert json.loads(journal_ran(project, home, SEED, start)) == [0, 0, 0], f"{start} writes its rows"
    installed(project, home, target)
    read = json.loads(journal_ran(project, home, READ))
    assert f"written on {start}" in read["task"] and f"planned on {start}" in read["plan"], f"{target} boots on the rows {start} wrote and lists its task and plan"
    assert f"said on {start}" in read["message"], f"{target} reads the message {start} wrote"
