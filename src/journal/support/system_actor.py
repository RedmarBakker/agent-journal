from typing import ClassVar

from journal.support.actor import Actor
from journal.support.actor_type import ActorType


class SystemActor(Actor):
    """The journal itself, acting on its own."""

    kind: ClassVar[ActorType] = ActorType.SYSTEM

    def is_system_actor(self) -> bool:
        return True
