from typing import ClassVar

from journal.support.actor import Actor
from journal.support.actor_type import ActorType


class PhoneActor(Actor):
    """The user's paired phone, by its number."""

    kind: ClassVar[ActorType] = ActorType.PHONE
