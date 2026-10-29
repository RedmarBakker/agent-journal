from dataclasses import dataclass

from journal.events.agent.agent_event import AgentEvent


@dataclass(frozen=True)
class SubagentStarted(AgentEvent):
    """The agent dispatched a subagent."""

    takes_remarks = False

    subagent: str
