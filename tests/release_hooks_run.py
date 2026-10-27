# Runs the post-commit and pre-push hooks in a scratch git repository as processes, so it is not in the default run: python3 -m pytest tests/release_hooks_run.py
"""A release commit whose version.py names another number is amended to carry the message's number, and a release tag is pushed only when its own update_steps.json names its version."""
import json
import subprocess
from pathlib import Path

import pytest

HOOK = Path(__file__).resolve().parents[1] / ".githooks" / "post-commit"
PRE_PUSH = Path(__file__).resolve().parents[1] / ".githooks" / "pre-push"
STEPS_REFUSAL = "push refused: the update_steps.json of v4.67.0"


def git(repo: Path, *words: str) -> str:
    return subprocess.run(["git", "-C", str(repo), "-c", "core.hooksPath=/dev/null", *words], capture_output=True, text=True, check=True, timeout=20).stdout


def test_a_release_commit_with_a_stale_version_is_amended_to_its_number(tmp_path: Path):
    repo = tmp_path / "repo"
    (repo / "src" / "journal").mkdir(parents=True)
    version = repo / "src" / "journal" / "version.py"
    version.write_text('VERSION = "4.55.2"\n')
    git(repo, "init", "-q")
    git(repo, "-c", "user.name=t", "-c", "user.email=t@example.com", "add", ".")
    git(repo, "-c", "user.name=t", "-c", "user.email=t@example.com", "commit", "-q", "-m", "4.55.3: the fix")
    ran = subprocess.run(["sh", str(HOOK)], cwd=repo, capture_output=True, text=True, timeout=20, env={"PATH": "/usr/bin:/bin:/usr/local/bin:/opt/homebrew/bin", "GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@example.com", "GIT_COMMITTER_NAME": "t", "GIT_COMMITTER_EMAIL": "t@example.com", "HOME": str(tmp_path)})
    assert ran.returncode == 0, ran.stderr
    assert 'VERSION = "4.55.3"' in git(repo, "show", "HEAD:src/journal/version.py"), "the commit itself carries the message's number"
    assert git(repo, "log", "--format=%s").splitlines() == ["4.55.3: the fix"], "amended, not a second commit"
    assert subprocess.run(["sh", str(HOOK)], cwd=repo, capture_output=True, text=True, timeout=20, env={"PATH": "/usr/bin:/bin:/usr/local/bin:/opt/homebrew/bin", "HOME": str(tmp_path)}).returncode == 0, "a matching version is left alone"



@pytest.mark.parametrize(("steps", "refused"), [({"4.66.0": {"step": True, "oldest": "4.61.0", "reason": "r"}}, True), ({"4.67.0": {"step": False, "reason": "r"}}, False)])
def test_a_release_tag_is_pushed_only_when_its_steps_file_names_its_version(tmp_path: Path, steps: dict, refused: bool):
    repo = tmp_path / "repo"
    repo.mkdir()
    (repo / "update_steps.json").write_text(json.dumps(steps))
    git(repo, "init", "-q")
    git(repo, "-c", "user.name=t", "-c", "user.email=t@example.com", "add", ".")
    git(repo, "-c", "user.name=t", "-c", "user.email=t@example.com", "commit", "-q", "-m", "4.67.0: the release")
    git(repo, "tag", "v4.67.0")
    sha = git(repo, "rev-parse", "v4.67.0").strip()
    ran = subprocess.run(["sh", str(PRE_PUSH)], cwd=repo, input=f"refs/tags/v4.67.0 {sha} refs/tags/v4.67.0 {'0' * 40}\n", capture_output=True, text=True, timeout=20, env={"PATH": "/usr/bin:/bin:/usr/local/bin:/opt/homebrew/bin", "HOME": str(tmp_path)})
    assert (STEPS_REFUSAL in ran.stderr) == refused, ran.stderr
    assert ("viewer_built" in ran.stderr) != refused, "a tag its file names goes on to the next check, the built viewer, which the scratch repository lacks"
