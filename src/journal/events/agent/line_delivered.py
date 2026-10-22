from dataclasses import dataclass, field
from typing import ClassVar

from journal.events.agent.agent_event import AgentEvent


@dataclass(frozen=True)
class LineDelivered(AgentEvent):
    """The journal sent the agent a line, by the key of the nudge that sent it, so a listener may count or record what was sent without sending a line of its own, which would send itself again."""

    answers_hook: ClassVar[bool] = False

    nudge: str
    values: dict = field(default_factory=dict)
