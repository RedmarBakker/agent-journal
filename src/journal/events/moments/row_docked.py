from dataclasses import dataclass

from journal.events.event import Event
from journal.models.support.ref import Ref
from journal.support.actor import Actor


@dataclass(frozen=True, kw_only=True)
class RowDocked(Event):
    """A row with no card in the chat is to be docked above it, so a card is written for it first."""

    environment_id: int
    row: Ref
    actor: Actor
