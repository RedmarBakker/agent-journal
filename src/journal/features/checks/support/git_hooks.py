import os
from pathlib import Path

from journal.config import Config
from journal.features.checks.support.git_hook import GitHook
from journal.features.git.support.git_facts import GitFacts

SHOWN_COMMANDS = 8
SAMPLE = ".sample"


class GitHooks:
    """The git hooks of the project's repository, from core.hooksPath or else .git/hooks, each by its name, active when it is present, executable and in the folder git uses, with the purpose its comments give and the commands it runs; read only, since git runs them at its own moments."""

    def __init__(self, config: Config) -> None:
        self.config = config

    def listed(self) -> list[GitHook]:
        folder = self.folder()
        if folder is None or not folder.is_dir():
            return []
        return [self.hook(path, folder) for path in sorted(folder.iterdir()) if self.is_hook(path)]

    @staticmethod
    def is_hook(path: Path) -> bool:
        return path.is_file() and not path.name.endswith(SAMPLE) and not path.name.startswith(".")

    def folder(self) -> Path | None:
        path = GitFacts.run(self.config.root, "rev-parse", "--git-path", "hooks")
        return (self.config.root / path).resolve() if path else None

    @staticmethod
    def hook(path: Path, folder: Path) -> GitHook:
        text = [line.strip() for line in path.read_text(errors="replace").splitlines()]
        comments = [line for line in text if line.startswith("#")]
        notes = [line.lstrip("#").strip() for line in comments if line[1:2] != "!"]
        steps = tuple(line for line in text if line and line not in comments)[:SHOWN_COMMANDS]
        return GitHook(path.name, os.access(path, os.X_OK), str(folder), " ".join(notes[:2]), steps)
