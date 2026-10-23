from dataclasses import dataclass


@dataclass(frozen=True)
class PinsData:
    """The pins feature's reading: the links pinned here, the links suggested within the last so many of the agent's own tool uses, and when the newest pin here was made, if one ever was."""

    pinned: tuple[str, ...]
    recent_suggestions: tuple[str, ...]
    newest_pin_at: float | None
