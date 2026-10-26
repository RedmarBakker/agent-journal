from typing import Protocol, runtime_checkable

from journal.events.agent.agent_event import AgentEvent


@runtime_checkable
class AgentEventAudience(Protocol):
    """Who hears an agent event the engine raises for a command: every listener for the main agent, and for a helper only the engine's own and those its file allows."""

    def dispatch(self, event: AgentEvent) -> list[object]: ...
