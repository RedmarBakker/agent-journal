from dataclasses import dataclass
from typing import ClassVar

from journal.events.agent.agent_event import AgentEvent


@dataclass(frozen=True)
class ImpasseReport(AgentEvent):
    """The agent reported with journal stuck that it is stuck, and why."""

    answers_hook: ClassVar[bool] = False

    reason: str
