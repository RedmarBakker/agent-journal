from argparse import Namespace

from journal.console.command import Command
from journal.features.git.support.launch_worktrees import LaunchWorktrees
from journal.features.git.support.worktree_removal import WorktreeRemoval
from journal.support.caller import Caller


class WorktreeCommand(Command):
    """The worktrees launches made, at .claude/worktrees, listed with those whose environment is gone, and the one way one is removed (WorktreeRemoval)."""

    noun = "worktree"

    def __init__(self, removal: WorktreeRemoval, worktrees: LaunchWorktrees) -> None:
        self.removal, self.worktrees = removal, worktrees

    def arguments(self, verbs) -> None:
        self.verb(verbs, "list", "the worktrees launches made, each with its branch, and those whose environment is gone marked so")
        self.verb(verbs, "remove", "remove a launch's worktree folder, keeping its branch and its last commit; refused while a session works in it or it holds uncommitted work").add_argument("name")

    def list(self, args: Namespace, caller: Caller) -> int:
        names, orphan_names = self.worktrees.names(), {tree.name for tree in self.worktrees.orphan_worktrees()}
        if not names:
            print("no launch worktree: journal claude --worktree <name> makes one")
        for name in names:
            tree = self.removal.worktree(name)
            print(f"{name}: on {tree.current_branch()}" + (f"; its environment is gone, journal worktree remove {name} removes it" if name in orphan_names else ""))
        return 0

    def remove(self, args: Namespace, caller: Caller) -> int:
        print(self.removal.removed(args.name))
        return 0
