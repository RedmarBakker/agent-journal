# This file starts real supervisors and journal servers for two worktree launches of one project, so it needs processes and is not in the default run: python3 -m pytest tests/worktree_launches_run.py
import json
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path
from urllib.error import HTTPError
from urllib.request import Request as HttpRequest, urlopen

import pytest

from journal.config import Config
from journal.launcher.launch import Launch
from journal.providers.support.status_line import StatusLine

PACKAGE = Path(__file__).resolve().parents[1] / "src"
NAMES = ("alpha", "beta")
WAIT_SECONDS = 60


def eventually(check, seconds: float = WAIT_SECONDS) -> bool:
    deadline = time.monotonic() + seconds
    while time.monotonic() < deadline:
        if check():
            return True
        time.sleep(0.2)
    return check()


def git(root: Path, *argv: str) -> subprocess.CompletedProcess:
    return subprocess.run(["git", *argv], cwd=root, capture_output=True, text=True, timeout=30)


def own_environ(root: Path, home: Path) -> dict[str, str]:
    """The test's own environment without the journal and agent this run is started under, for a journal of its own on root, on a free port."""
    kept = {key: value for key, value in os.environ.items() if not key.startswith(("JOURNAL_", "SUPERVISOR_", "CLAUDE")) and key != "AGENT_JOURNAL_ACTIVE"}
    return {**kept, "JOURNAL_ROOT": str(root), "JOURNAL_PORT": "0", "HOME": str(home), "CLAUDE_CONFIG_DIR": str(home / ".claude"), "PYTHONPATH": str(PACKAGE)}


def launched(root: Path, home: Path, name: str) -> tuple[subprocess.Popen, dict]:
    """A real supervisor for a worktree launch, from the launch file the launcher writes, with cat standing in for the agent in front."""
    launcher = Launch.parse(["claude", "--worktree", name], root)
    choice = launcher.choice()
    launch = launcher.chosen(choice).launch_file(choice, StatusLine(root))
    environ = {**own_environ(root, home), "JOURNAL_ENV": name, "JOURNAL_LAUNCH": launch["launch"]}
    launch["front"] = {**launch["front"], "command": ["cat"], "resume": [], "env": environ}
    launch["services"] = [{**service, "env": {**service["env"], **environ}} for service in launch["services"]]
    launch["owner"] = os.getpid()
    path = root / ".journal" / "runtime" / "launches" / f"{name}.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(launch))
    process = subprocess.Popen([sys.executable, "-m", "supervisor", str(path)], cwd=root, env=environ, stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=open(root / ".journal" / "runtime" / f"supervisor-{name}.err", "a"))
    return process, launch


def answering(root: Path) -> bool:
    try:
        with urlopen(f"http://127.0.0.1:{Config(root).stored_port()[0]}/journal/health", timeout=1):
            return True
    except (OSError, IndexError):
        return False


def posted(root: Path, path: str, body: dict, headers: dict[str, str]) -> dict:
    request = HttpRequest(f"http://127.0.0.1:{Config(root).stored_port()[0]}{path}", data=json.dumps(body).encode(), method="POST", headers={"Content-Type": "application/json", **headers})
    try:
        with urlopen(request, timeout=10) as answer:
            return json.loads(answer.read() or b"{}")
    except HTTPError as refused:
        raise AssertionError(f"{path} answered {refused.code}: {refused.read().decode()}") from None


def ended(process: subprocess.Popen) -> None:
    if process.poll() is None:
        process.terminate()
    try:
        process.wait(20)
    except subprocess.TimeoutExpired:
        process.kill()
        process.wait(5)


@pytest.mark.timeout(300)
def test_two_real_worktree_launches_share_one_journal_survive_an_end_a_clean_up_and_a_delete_and_relaunch_into_the_same_folders(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    if shutil.which("git") is None:
        pytest.skip("git is not installed, so no worktree can be made")
    root, home = tmp_path / "project", tmp_path / "home"
    root.mkdir()
    (home / ".claude").mkdir(parents=True)
    for key in [key for key in os.environ if key.startswith(("JOURNAL_", "SUPERVISOR_", "CLAUDE")) or key == "AGENT_JOURNAL_ACTIVE"]:
        monkeypatch.delenv(key)
    for key, value in own_environ(root, home).items():
        monkeypatch.setenv(key, value)
    for argv in (["init", "-q", "-b", "main"], ["-c", "user.email=t@t", "-c", "user.name=t", "commit", "-q", "--allow-empty", "-m", "start"]):
        git(root, *argv)
    real_state = Path.home() / ".claude.json"
    real_time = real_state.stat().st_mtime_ns if real_state.exists() else 0
    supervisors: dict[str, subprocess.Popen] = {}
    launches: dict[str, dict] = {}
    try:
        for name in NAMES:
            supervisors[name], launches[name] = launched(root, home, name)
        assert eventually(lambda: answering(root)), "one journal server answers for both launches"
        assert Config(root).stored_port()[0] not in range(8420, 8430), "on a port outside the person's own"
        for name in NAMES:
            posted(root, "/hooks/claude", {"hook_event_name": "SessionStart", "session_id": f"session-{name}"}, {"X-Journal-Env": name, "X-Journal-Launch": launches[name]["launch"]})
        folders = {name: root / ".claude" / "worktrees" / name for name in NAMES}
        tips = {name: git(folders[name], "rev-parse", "HEAD").stdout.strip() for name in NAMES}
        assert all(folder.is_dir() for folder in folders.values()) and all(git(folders[name], "rev-parse", "--abbrev-ref", "HEAD").stdout.strip() == f"worktree-{name}" for name in NAMES), "each launch works in its own worktree on its own branch"
        ended(supervisors.pop("alpha"))
        assert eventually(lambda: answering(root), 20), "the other launch's journal answers once the first launch ends"
        environments = json.loads(urlopen(HttpRequest(f"http://127.0.0.1:{Config(root).stored_port()[0]}/journal/environments", headers={"X-Journal-Env": "beta"}), timeout=10).read())["rows"]
        alpha = next(row for row in environments if row["name"] == "alpha")
        posted(root, f"/journal/environments/{alpha['id']}/remove", {}, {"X-Journal-Env": "beta"})
        assert folders["alpha"].is_dir() and git(root, "rev-parse", "--verify", "-q", "worktree-alpha").returncode == 0, "deleting an environment keeps its worktree and its branch"
        supervisors["alpha"], launches["alpha"] = launched(root, home, "alpha")
        assert eventually(lambda: answering(root)), "the journal answers after the relaunch"
        assert all(git(folders[name], "rev-parse", "HEAD").stdout.strip() == tips[name] for name in NAMES), "both launches find their folders where they left them, at the same commit"
    finally:
        for process in supervisors.values():
            ended(process)
    assert (real_state.stat().st_mtime_ns if real_state.exists() else 0) == real_time, "the person's own Claude Code state is never touched"
