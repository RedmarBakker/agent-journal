from typing import ClassVar

from journal.support.actor import Actor
from journal.support.actor_type import ActorType


class UserActor(Actor):
    """A user, by their account number."""

    kind: ClassVar[ActorType] = ActorType.USER
