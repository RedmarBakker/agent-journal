import subprocess
from pathlib import Path

GIT_SECONDS = 10
JOURNAL = ".journal"


class InnerRepositories:
    """The git repositories a project folder holds inside it, each at the top of a folder of its own: those its own repository ignores when the project is one, every one of them when the project folder is none; workers and launch worktrees read them alike."""

    def __init__(self, root: Path) -> None:
        self.root = root

    def names(self) -> tuple[str, ...]:
        is_repository = self.git(self.root, "rev-parse", "--git-dir").returncode == 0
        return tuple(sorted(child.name for child in self.root.iterdir() if self.is_inner(child, is_repository)))

    def is_inner(self, child: Path, is_repository: bool) -> bool:
        if not child.is_dir() or child.is_symlink() or not (child / ".git").exists() or child.name == JOURNAL:
            return False
        if is_repository and self.git(self.root, "check-ignore", "-q", child.name).returncode != 0:
            return False
        top = self.git(child, "rev-parse", "--show-toplevel")
        return top.returncode == 0 and Path(top.stdout.strip()).resolve() == child.resolve()

    @staticmethod
    def git(folder: Path, *argv: str) -> subprocess.CompletedProcess:
        return subprocess.run(["git", "-C", str(folder), *argv], capture_output=True, text=True, timeout=GIT_SECONDS)
