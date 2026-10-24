from dataclasses import dataclass

from journal.events.event import Event
from journal.models.support.ref import Ref


@dataclass(frozen=True, kw_only=True)
class SharedCommentLeft(Event):
    """A visitor left a comment under what a share link opens: who, what they wrote and the row it is under."""

    environment_id: int
    share: int
    row: Ref
    name: str
    text: str
