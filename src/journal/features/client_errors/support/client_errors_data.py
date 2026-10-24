from dataclasses import dataclass


@dataclass(frozen=True)
class ClientErrorsData:
    """How many distinct viewer errors are unhandled, and whether the agent was told of them within the last so many of its tool uses."""

    count: int = 0
    is_reported: bool = False
