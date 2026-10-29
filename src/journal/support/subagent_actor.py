from typing import ClassVar

from journal.support.actor import SUBAGENT_SEPARATOR, Actor
from journal.support.actor_type import ActorType


class SubagentActor(Actor):
    """A subagent an agent started, by its agent's session and its own joined by a colon."""

    kind: ClassVar[ActorType] = ActorType.AGENT

    @classmethod
    def fits(cls, actor_type: ActorType, id: str) -> bool:
        return actor_type == cls.kind and SUBAGENT_SEPARATOR in id

    def rule_maker[T](self, agent_way: T, person_way: T) -> T:
        return agent_way
