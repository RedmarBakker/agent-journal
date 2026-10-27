from dataclasses import dataclass

from journal.events.agent.agent_event import AgentEvent


@dataclass(frozen=True)
class JournalReturned(AgentEvent):
    """A worker's hook is answered after its journal stopped answering it at silence_start."""

    silence_start: float = 0.0
