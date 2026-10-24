from dataclasses import dataclass

from journal.events.event import Event


@dataclass(frozen=True, kw_only=True)
class ReaderAdded(Event):
    """A reader was added or revised, so the cards of the outputs it reads show what it picks now."""

    reader: str
