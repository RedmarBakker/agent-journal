from dataclasses import dataclass
from typing import ClassVar

from journal.events.agent.agent_event import AgentEvent


@dataclass(frozen=True)
class RoleTaken(AgentEvent):
    """The agent took on a Role for its next step with journal role take, by the Role's id."""

    answers_hook: ClassVar[bool] = False

    role: str
