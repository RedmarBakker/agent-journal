from dataclasses import dataclass
from typing import ClassVar

from journal.events.agent.agent_event import AgentEvent


@dataclass(frozen=True)
class RoleStepEnded(AgentEvent):
    """The agent ended the step it worked as a Role with journal role done."""

    answers_hook: ClassVar[bool] = False
