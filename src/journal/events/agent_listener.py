from typing import ClassVar, TypeVar

from journal.events.agent.agent_event import AgentEvent
from journal.events.listener import Listener
from journal.support.decision import Decision

E = TypeVar("E", bound=AgentEvent)


class AgentListener(Listener[E]):
    """A feature's handler for one agent event. It runs after the server replies unless its feature names it among its answer_listeners, with the reason it runs before the answer."""

    free_request: ClassVar[bool] = False

    def handle(self, event: E) -> Decision | None:
        return None
