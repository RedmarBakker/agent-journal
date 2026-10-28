from typing import ClassVar, TypeVar

from journal.events.agent.agent_event import AgentEvent
from journal.events.blocking import Blocking
from journal.events.listener import Listener
from journal.support.decision import Decision

E = TypeVar("E", bound=AgentEvent)


class AgentListener(Listener[E]):
    """E feature's handler for one agent event. Deferred by default: the server replies first and runs it after. E handler that must run before the agent goes on says why with blocking = Blocking.ANSWER, its result being part of the answer, or Blocking.NEXT_DECISION, a row the next decision reads; a handler that only updates the viewer never blocks."""

    blocking: ClassVar[Blocking | None] = None
    free_request: ClassVar[bool] = False

    def handle(self, event: E) -> Decision | None:
        return None
