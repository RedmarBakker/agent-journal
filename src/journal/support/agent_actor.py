from typing import ClassVar

from journal.support.actor import SUBAGENT_SEPARATOR, Actor
from journal.support.actor_type import ActorType


class AgentActor(Actor):
    """An agent, by its session."""

    kind: ClassVar[ActorType] = ActorType.AGENT

    @classmethod
    def fits(cls, actor_type: ActorType, id: str) -> bool:
        return actor_type == cls.kind and SUBAGENT_SEPARATOR not in id

    def rule_maker[T](self, agent_way: T, person_way: T) -> T:
        return agent_way

    def is_agent_or_subagent(self) -> bool:
        return True
