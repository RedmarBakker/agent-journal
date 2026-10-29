from typing import ClassVar

from journal.support.actor import Actor
from journal.support.actor_type import ActorType


class ReviewerActor(Actor):
    """A reviewer the journal sent, by its number."""

    kind: ClassVar[ActorType] = ActorType.REVIEWER
