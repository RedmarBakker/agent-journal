from dataclasses import dataclass


@dataclass(frozen=True)
class SilentRun:
    """A command of the agent's running in the background that has printed no new line for a while, by its output number, its line and how long it has been quiet."""

    output: int
    command: str
    quiet_seconds: int
