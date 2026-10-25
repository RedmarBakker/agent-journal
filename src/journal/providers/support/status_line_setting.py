from typing import TypedDict


class StatusLineSetting(TypedDict):
    """The status line entry of an agent's settings file."""

    type: str
    command: str
    padding: int
