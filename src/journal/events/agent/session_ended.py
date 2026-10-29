from dataclasses import dataclass

from journal.events.agent.agent_event import AgentEvent


@dataclass(frozen=True)
class SessionEnded(AgentEvent):
    """The conversation ended."""

    takes_remarks = False
    is_turn_end = True

