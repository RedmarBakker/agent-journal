from dataclasses import dataclass


@dataclass(frozen=True)
class MarkGroup:
    """A group of chat mark kinds as Show in chat lists them, with the switch that turns all of them on or off."""

    key: str
    title: str
    icon: str
