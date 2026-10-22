class WorktreeFailure(Exception):
    """git refused to create the worktree a launch requested, with git's message."""

    def __init__(self, name: str, line_text: str) -> None:
        super().__init__(f"the worktree {name} could not be made: {line_text}")
