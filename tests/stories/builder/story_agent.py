from dataclasses import dataclass

from journal.support.actor import Actor
from journal.support.agent_role import AgentRole


@dataclass(frozen=True)
class StoryAgent:
    """One agent a story names as the first argument of a step or a check: its role, helper row number, subagent id, plugin actor, and credentials."""

    role: AgentRole
    number: int = 0
    agent_id: str = ""
    session: str = ""
    actor: Actor | None = None
    credential: str = ""
    grant_credential: str = ""

    def __str__(self) -> str:
        return str(self.number)

    def __int__(self) -> int:
        return self.number

    def __index__(self) -> int:
        return self.number
