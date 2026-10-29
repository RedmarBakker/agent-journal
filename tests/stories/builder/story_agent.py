from dataclasses import dataclass

from journal.support.agent_role import AgentRole


@dataclass(frozen=True)
class StoryAgent:
    """One agent a story names as the first argument of a step or a check: its role, for a helper its row number, which it reads as wherever a number is written, and for a subagent the agent id its hooks carry."""

    role: AgentRole
    number: int = 0
    agent_id: str = ""

    def __str__(self) -> str:
        return str(self.number)

    def __int__(self) -> int:
        return self.number

    def __index__(self) -> int:
        return self.number
