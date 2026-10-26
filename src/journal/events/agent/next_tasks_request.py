from dataclasses import dataclass

from journal.events.agent.agent_event import AgentEvent


@dataclass(frozen=True)
class NextTasksRequest(AgentEvent):
    """The agent asked for the next tasks it is to hand out, as the orchestrator does before it gives work to workers."""
