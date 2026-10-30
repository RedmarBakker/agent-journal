from dataclasses import dataclass

from journal.support.operation import Operation


@dataclass(frozen=True)
class AgentMessage(Operation):
    """A message the agent sends another agent or one of its subagents with its program's own tool, with the short summary of it the tool asks for."""

    operation_type = "agent message"
    receiver: str
    text: str
    summary: str = ""
