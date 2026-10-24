from dataclasses import dataclass

from journal.support.actor import Actor
from journal.support.card_kind import CardKind


@dataclass(frozen=True)
class ProcessMark:
    """What a process card is to show now: its process, its key, its label and data, whom it is written as, and whether its process still runs; written by a listener through ProcessCards."""

    process: str
    environment_id: int
    key: str
    label: str
    data: dict
    actor: Actor
    shows: CardKind
    active: bool
    detail: str = ""
    session: str | None = None
