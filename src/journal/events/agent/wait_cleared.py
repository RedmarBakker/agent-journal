from dataclasses import dataclass
from typing import ClassVar

from journal.events.agent.agent_event import AgentEvent


@dataclass(frozen=True)
class WaitCleared(AgentEvent):
    """The agent cleared its wait with journal await clear, so it waits for nothing any more."""

    answers_hook: ClassVar[bool] = False
