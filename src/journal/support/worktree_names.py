import random
from pathlib import Path

# the words a worktree's made-up name is put together from, one of each
NAME_WORDS = (("amber", "brisk", "calm", "deft", "eager", "fond", "gentle", "hardy", "keen", "lucid", "mellow", "nimble", "quiet", "rapid", "steady", "vivid"),
              ("otter", "heron", "maple", "cedar", "falcon", "harbor", "lantern", "meadow", "orchid", "pebble", "quartz", "river", "sparrow", "thistle", "willow", "zephyr"))


class WorktreeNames:
    """A name for a worktree a launch makes when it is given none: two words no worktree of the project holds yet, so two launches never share one folder."""

    def __init__(self, root: Path) -> None:
        self.root = root

    def unused(self) -> str:
        folder = self.root / ".claude" / "worktrees"
        taken = {path.name for path in folder.iterdir()} if folder.is_dir() else set()
        names = [f"{first}-{second}" for first in NAME_WORDS[0] for second in NAME_WORDS[1]]
        random.shuffle(names)
        return next((name for name in names if name not in taken), f"worktree-{len(taken) + 1}")
