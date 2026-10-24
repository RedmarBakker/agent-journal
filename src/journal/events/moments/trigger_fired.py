from dataclasses import dataclass

from journal.events.event import Event
from journal.models.support.ref import Ref


@dataclass(frozen=True, kw_only=True)
class TriggerFired(Event):
    """Words matched a trigger, in the session and environment they appeared in."""

    environment_id: int
    session: str
    text: str
    phrases: tuple[str, ...]
    ref: Ref
