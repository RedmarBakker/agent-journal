from journal.events.agent.session_started import SessionStarted
from journal.events.agent_listener import AgentListener
from journal.features.memory.support.memory_context import MemoryContext
from journal.support.actor import Actor
from journal.events.blocking import Blocking


class StartMemory(AgentListener[SessionStarted]):
    """The start block gives the agent every rule and reminder, so at a session start, new or after a compaction, every one is in its context window."""

    blocking = Blocking.ANSWER

    def __init__(self, context: MemoryContext) -> None:
        self.context = context

    def handle(self, event: SessionStarted) -> None:
        if not event.subagent:
            self.context.admit_all(Actor.system())
