from dataclasses import dataclass
from typing import ClassVar

from journal.events.agent.agent_event import AgentEvent


@dataclass(frozen=True)
class WaitRequest(AgentEvent):
    """The agent reported with journal await that it is waiting for something outside its control."""

    answers_hook: ClassVar[bool] = False

    focus: str
    end_refs: str = ""

    def wait_terms(self) -> tuple[str, str, float]:
        return self.focus, self.end_refs, self.time
