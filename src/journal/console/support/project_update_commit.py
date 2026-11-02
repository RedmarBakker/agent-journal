import subprocess
from pathlib import Path

from journal.config import Config

GIT_SECONDS = 10


class ProjectUpdateCommit:
    """Commits only the project files written by journal setup during an update."""

    def __init__(self, config: Config) -> None:
        self.config = config

    def commit(self, files: list[Path], release: str) -> list[str]:
        paths = self.pathspecs(files)
        if not release or not paths or self.git("rev-parse", "--show-toplevel").returncode:
            return []
        paths = self.not_ignored(paths)
        if not paths:
            return []
        self.answered(self.git("add", "--", *paths))
        changed = self.changed(paths)
        if not changed:
            return []
        message = f"Update the journal to {release}"
        self.answered(self.git("commit", "--only", "-m", message, "--", *changed))
        return changed

    def pathspecs(self, files: list[Path]) -> list[str]:
        return sorted({path.relative_to(self.config.root).as_posix() for path in files})

    def not_ignored(self, paths: list[str]) -> list[str]:
        result = self.git("check-ignore", "-z", "--stdin", given="".join(f"{path}\0" for path in paths))
        if result.returncode not in (0, 1):
            self.answered(result)
        ignored = set(result.stdout.split("\0"))
        return [path for path in paths if path not in ignored]

    def changed(self, paths: list[str]) -> list[str]:
        result = self.answered(self.git("diff", "--cached", "--no-renames", "--name-only", "-z", "--", *paths))
        return sorted(path for path in result.stdout.split("\0") if path)

    def git(self, *arguments: str, given: str = "") -> subprocess.CompletedProcess:
        return subprocess.run(["git", "-C", str(self.config.root), *arguments], input=given, capture_output=True, text=True, timeout=GIT_SECONDS)

    @staticmethod
    def answered(result: subprocess.CompletedProcess) -> subprocess.CompletedProcess:
        if result.returncode:
            raise RuntimeError(result.stderr.strip() or "git refused the journal update commit")
        return result
