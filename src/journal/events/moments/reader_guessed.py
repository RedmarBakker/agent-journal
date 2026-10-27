from dataclasses import dataclass

from journal.events.event import Event


@dataclass(frozen=True, kw_only=True)
class ReaderGuessed(Event):
    """The journal saved a reader on its own for a run moved to the background: the reader, the command it reads and the output it was made from."""

    environment_id: int
    session: str | None
    reader: str
    command: str
    output: int
    subject: str
