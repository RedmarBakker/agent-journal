from dataclasses import dataclass


@dataclass(frozen=True)
class UpdateTarget:
    """What an update moves the journal to: the git ref the installer takes, a release's tag or a branch, its label in the chat and the mark, and why it is installed, as the update log says."""

    ref: str
    label: str
    reason: str = ""
