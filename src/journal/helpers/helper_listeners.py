from journal.events.agent.agent_event import AgentEvent
from journal.events.bus import Bus
from journal.events.listener import Listener
from journal.features.registry import Registry
from journal.models.agent_role import AgentRole
from journal.repositories.agents import Agents


class HelperListeners:
    """The one funnel for an agent event raised by or for a helper, its hooks and its commands alike: only the engine's own listeners and those its file allows, by their own class or their feature's, hear it; the main agent's events reach every listener."""

    def __init__(self, bus: Bus, registry: Registry, agents: Agents) -> None:
        self.bus, self.registry, self.agents = bus, registry, agents

    def listeners(self, event: AgentEvent) -> list[Listener]:
        bus_listeners, role = self.bus.listeners(type(event)), self.role(event)
        if not role.is_helper():
            return bus_listeners
        return [listener for listener in bus_listeners if self.registry.reaches_helper(listener.registered_class(), role)]

    def dispatch(self, event: AgentEvent) -> list[object]:
        return [listener.handle(event) for listener in self.listeners(event)]

    def role(self, event: AgentEvent) -> AgentRole:
        rows = self.agents.session_rows(event.session) if event.session else []
        return rows[0].role if rows else AgentRole.MAIN
