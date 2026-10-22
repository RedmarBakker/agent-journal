from dataclasses import dataclass


@dataclass(frozen=True)
class Option:
    """One line of a menu: its text, the badges after it, and whether it is separated from the lines above it by a blank line."""

    label: str
    badges: tuple[str, ...] = ()
    separate: bool = False
