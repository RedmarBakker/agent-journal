from dataclasses import dataclass
from typing import ClassVar

from journal.events.agent.agent_event import AgentEvent


@dataclass(frozen=True)
class RoleTaken(AgentEvent):
    """The agent took on a Role for its next step with journal role take, by its id and the plan task it works on."""

    answers_hook: ClassVar[bool] = False

    role: str
    task_id: int = 0
