from typing import ClassVar

from journal.support.actor import Actor
from journal.support.actor_type import ActorType


class ExternalActor(Actor):
    """An agent of another project, by its name."""

    kind: ClassVar[ActorType] = ActorType.EXTERNAL
