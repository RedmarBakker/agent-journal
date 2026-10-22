from dataclasses import dataclass

from journal.events.agent.agent_event import AgentEvent
from journal.support.tool_call import ToolCall


@dataclass(frozen=True)
class ToolFailed(AgentEvent):
    """A tool that started ended in an error and returned no result: the same reading of the call as when it started, with the error as the tool reported it."""

    is_work = True

    call: ToolCall
    error: str

    def recorded(self) -> dict:
        return {"call": self.call.as_data()}
