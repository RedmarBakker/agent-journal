from dataclasses import dataclass

from journal.events.agent.agent_event import AgentEvent


@dataclass(frozen=True)
class SubagentEnded(AgentEvent):
    """A subagent reported back, with its last output."""

    takes_remarks = False

    subagent: str
    report: str = ""
