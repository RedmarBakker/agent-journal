from dataclasses import dataclass


@dataclass(frozen=True)
class GitFinished:
    """What a git or gh command printed and whether it succeeded; a command that could not run or ran too long has not succeeded and printed nothing."""

    succeeded: bool
    text: str
