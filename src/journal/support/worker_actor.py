from typing import ClassVar

from journal.support.actor import Actor
from journal.support.actor_type import ActorType


class WorkerActor(Actor):
    """A worker the main agent sent, by its number."""

    kind: ClassVar[ActorType] = ActorType.WORKER
