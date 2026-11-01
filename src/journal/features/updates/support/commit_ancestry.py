import hashlib
import subprocess
from pathlib import Path

from journal.config import Config

GIT_SECONDS = 60


class CommitAncestry:
    """Fetches commit-only branch history into the journal's update cache to check ancestry."""

    def __init__(self, config: Config) -> None:
        self.config = config

    def is_newer(self, head: str, installed: str, repository: str, branch: str) -> bool:
        if not installed:
            return True
        database = self.database(repository)
        self.prepare(database)
        self.fetch(database, repository, branch)
        self.require_commit(database, installed, "installed", repository, branch)
        self.require_commit(database, head, "branch head", repository, branch)
        return self.cache_ancestor(database, installed, head)

    def database(self, repository: str) -> Path:
        key = hashlib.sha256(repository.encode()).hexdigest()
        return self.config.home / "runtime" / "update-ancestry" / f"{key}.git"

    def prepare(self, database: Path) -> None:
        if (database / "config").is_file():
            return
        database.parent.mkdir(parents=True, exist_ok=True)
        result = subprocess.run(
            ["git", "init", "--bare", "--quiet", str(database)],
            cwd=self.config.home, capture_output=True, text=True, timeout=GIT_SECONDS,
        )
        if result.returncode:
            detail = (result.stderr or result.stdout).strip()
            raise OSError(f"could not create the journal's commit cache: {detail[-300:] or result.returncode}")

    def fetch(self, database: Path, repository: str, branch: str) -> None:
        branch_key = hashlib.sha256(branch.encode()).hexdigest()
        destination = f"refs/heads/update/{branch_key}"
        result = subprocess.run(
            ["git", f"--git-dir={database}", "fetch", "--quiet", "--filter=tree:0", "--no-tags",
             repository, f"+refs/heads/{branch}:{destination}"],
            cwd=self.config.home, capture_output=True, text=True, timeout=GIT_SECONDS,
        )
        if result.returncode:
            detail = (result.stderr or result.stdout).strip()
            raise OSError(
                f"could not fetch commit history for branch {branch} from {repository}: "
                f"{detail[-300:] or result.returncode}"
            )

    def require_commit(self, database: Path, commit: str, name: str, repository: str, branch: str) -> None:
        result = subprocess.run(
            ["git", f"--git-dir={database}", "cat-file", "-e", f"{commit}^{{commit}}"],
            cwd=self.config.home, capture_output=True, text=True, timeout=GIT_SECONDS,
        )
        if result.returncode:
            raise OSError(f"the {name} {commit[:12]} is not available from branch {branch} of {repository}")

    def cache_ancestor(self, database: Path, installed: str, head: str) -> bool:
        result = subprocess.run(
            ["git", f"--git-dir={database}", "merge-base", "--is-ancestor", installed, head],
            cwd=self.config.home, capture_output=True, text=True, timeout=GIT_SECONDS,
        )
        if result.returncode == 1:
            return False
        if result.returncode:
            detail = (result.stderr or result.stdout).strip()
            raise OSError(f"could not compare the installed commit with the branch head: {detail[-300:] or result.returncode}")
        return True
