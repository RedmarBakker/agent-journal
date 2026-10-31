from dataclasses import dataclass


@dataclass(frozen=True)
class Choice:
    """What the boot menu decided: the environment, the session to resume (empty for a new conversation), whether other hooks are set aside, whether the agent asks before each tool, and whether the environment needs its own worktree."""

    environment: str
    resume: str = ""
    stashed_hooks: bool = False
    prompt_flags: bool = False
    worktree: bool = False
