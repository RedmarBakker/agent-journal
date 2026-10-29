from journal.events.agent.agent_event import AgentEvent
from journal.events.bus import Bus
from journal.events.listener import Listener
from journal.features.registry import Registry


class RoleListeners:
    """The one funnel for an agent event, its hooks and its commands alike: the listeners its agent's role file lets reach it hear it, every one for the main agent, the engine's own and those its file allows for a helper."""

    def __init__(self, bus: Bus, registry: Registry) -> None:
        self.bus, self.registry = bus, registry

    def listeners(self, event: AgentEvent) -> list[Listener]:
        return [*self.answer_listeners(event), *self.background_listeners(event)]

    def answer_listeners(self, event: AgentEvent) -> list[Listener]:
        return self.reaching(event, self.bus.answer_listeners(type(event)))

    def background_listeners(self, event: AgentEvent) -> list[Listener]:
        return self.reaching(event, self.bus.background_listeners(type(event)))

    def reaching(self, event: AgentEvent, bus_listeners: list[Listener]) -> list[Listener]:
        return [listener for listener in bus_listeners if self.registry.reaches_helper(listener.registered_class(), event.agent.role)]

    def dispatch(self, event: AgentEvent) -> list[object]:
        return [listener.handle(event) for listener in self.listeners(event)]
