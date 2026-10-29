from typing import ClassVar

from journal.support.actor import SUBAGENT_SEPARATOR, Actor
from journal.support.actor_type import ActorType


class AgentActor(Actor):
    """An agent, by its session."""

    kind: ClassVar[ActorType] = ActorType.AGENT

    @classmethod
    def fits(cls, actor_type: ActorType, id: str) -> bool:
        return actor_type == cls.kind and SUBAGENT_SEPARATOR not in id
