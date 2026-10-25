from dataclasses import dataclass

from journal.events.event import Event
from journal.models.model import Model
from journal.support.actor import Actor


@dataclass(frozen=True)
class Purged(Event):
    """Rows of one model were deleted together, without a Deleted for each: the rows as they were stored and who deleted them."""

    model: type[Model]
    rows: tuple[Model, ...]
    actor: Actor
