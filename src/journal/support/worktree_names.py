import random
import subprocess
from pathlib import Path

from journal.support.worktree_refs import TIPS_REF

GIT_SECONDS = 10

# the words a worktree's made-up name is put together from, one of each
NAME_PARTS = (("amber", "brisk", "calm", "deft", "eager", "fond", "gentle", "hardy", "keen", "lucid", "mellow", "nimble", "quiet", "rapid", "steady", "vivid"),
              ("otter", "heron", "maple", "cedar", "falcon", "harbor", "lantern", "meadow", "orchid", "pebble", "quartz", "river", "sparrow", "thistle", "willow", "zephyr"))


class WorktreeNames:
    """A name for a worktree a launch makes when it is given none: two words no worktree folder, worktree branch, kept tip or environment of the project holds yet, so a new launch never shares a folder or takes over old work or a conversation."""

    def __init__(self, root: Path) -> None:
        self.root = root

    def unused(self, environments: set[str]) -> str:
        used_names = {*self.folder_names(), *self.ref_names(), *environments}
        names = [f"{first}-{second}" for first in NAME_PARTS[0] for second in NAME_PARTS[1]]
        random.shuffle(names)
        return next((name for name in names if name not in used_names), next(f"spare-{number}" for number in range(1, len(used_names) + 2) if f"spare-{number}" not in used_names))

    def folder_names(self) -> set[str]:
        folder = self.root / ".claude" / "worktrees"
        return {path.name for path in folder.iterdir()} if folder.is_dir() else set()

    # a branch worktree-<name> or a kept tip that outlived its worktree would hand a new launch the old work
    def ref_names(self) -> set[str]:
        listed = subprocess.run(["git", "-C", str(self.root), "for-each-ref", "--format=%(refname)", "refs/heads/worktree-*", f"{TIPS_REF}/"], capture_output=True, text=True, timeout=GIT_SECONDS)
        return {line.removeprefix("refs/heads/worktree-").removeprefix(f"{TIPS_REF}/") for line in listed.stdout.splitlines()}
