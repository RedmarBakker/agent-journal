from journal.config import Config
from journal.repositories.environments import Environments
from journal.support.worktree import Worktree

LAUNCH_FOLDER = ".claude/worktrees"
# a folder an older version moved aside, named <name>.moved-aside-<time>; it is no launch worktree
RENAMED_TAG = ".moved-aside-"


class LaunchWorktrees:
    """The worktrees launches made at .claude/worktrees, and those of them whose environment is gone, which no environment lists any more."""

    def __init__(self, config: Config, environments: Environments) -> None:
        self.config, self.environments = config, environments

    def names(self) -> list[str]:
        folder = self.config.root / LAUNCH_FOLDER
        if not folder.is_dir():
            return []
        return sorted(path.name for path in folder.iterdir() if path.is_dir() and RENAMED_TAG not in path.name)

    def orphan_worktrees(self) -> list[Worktree]:
        return [Worktree(self.config.root, name) for name in self.names() if not self.environments.matching(name=name)]
