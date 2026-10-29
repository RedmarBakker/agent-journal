from dataclasses import dataclass
from typing import Callable

from journal.models.agent import Agent
from journal.support.actor import Actor
from journal.support.agent_role import AgentRole


@dataclass(frozen=True)
class Origin:
    """Where a piece of work came from: its environment, who acts, in which role, from which session, and the agent row found for it."""

    environment: Callable[[], int]
    actor: Actor
    role: AgentRole
    session: str | None = None
    agent: Agent | None = None

    @classmethod
    def agent_origin(cls, agent: Agent, actor: Actor) -> "Origin":
        return cls(lambda: agent.environment_id, actor, agent.role, agent.session, agent)

    @classmethod
    def person_origin(cls, environment: Callable[[], int], actor: Actor) -> "Origin":
        return cls(environment, actor, AgentRole.MAIN)
