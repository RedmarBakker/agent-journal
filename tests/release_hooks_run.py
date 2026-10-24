# Runs the post-commit hook in a scratch git repository as a process, so it is not in the default run: python3 -m pytest tests/release_hooks_run.py
"""A release commit whose version.py names another number is amended to carry the message's number."""
import subprocess
from pathlib import Path

HOOK = Path(__file__).resolve().parents[1] / ".githooks" / "post-commit"


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
