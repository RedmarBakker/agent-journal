from typing import TypedDict


class CommandEnvironment(TypedDict):
    """The environment a journal command runs in: the root it works on and the path it finds programs by."""

    JOURNAL_ROOT: str
    PATH: str
