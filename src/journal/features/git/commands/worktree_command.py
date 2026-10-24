from argparse import Namespace

from journal.console.command import Command
from journal.features.git.support.worktree_removal import WorktreeRemoval
from journal.support.caller import Caller


class WorktreeCommand(Command):
    """The worktrees launches made, at .claude/worktrees, and the one way one is removed (WorktreeRemoval)."""

    noun = "worktree"

    def __init__(self, removal: WorktreeRemoval) -> None:
        self.removal = removal

    def arguments(self, verbs) -> None:
        self.verb(verbs, "remove", "remove a launch's worktree folder, keeping its branch and its last commit; refused while a session works in it or it holds uncommitted work").add_argument("name")

    def remove(self, args: Namespace, caller: Caller) -> int:
        print(self.removal.removed(args.name))
        return 0
