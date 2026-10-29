from typing import ClassVar

from journal.support.actor import Actor
from journal.support.actor_type import ActorType


class VerifierActor(Actor):
    """A verifier the journal sent, by its number."""

    kind: ClassVar[ActorType] = ActorType.VERIFIER
