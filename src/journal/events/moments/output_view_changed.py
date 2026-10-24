from dataclasses import dataclass

from journal.events.event import Event


@dataclass(frozen=True, kw_only=True)
class OutputViewChanged(Event):
    """What a watched or background output's card shows changed since the card was written, as its files were read again."""

    environment_id: int
    output: int
