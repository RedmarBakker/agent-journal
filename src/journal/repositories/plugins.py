from journal.support.agent_role import AgentRole
from journal.db.connection import Connection
from journal.events.bus import Bus
from journal.models.plugin import Plugin
from journal.support.actor import Actor
from journal.repositories.repository import Repository
from journal.support.time_source import TimeSource


class Plugins(Repository[Plugin]):
    """The plugins installed in the project, one row each, the same for every environment."""

    model = Plugin

    def __init__(self, connection: Connection, bus: Bus, time_source: TimeSource) -> None:
        super().__init__(connection, bus, time_source)
        self.live: list[Plugin] | None = None

    def save(self, row: Plugin, actor: Actor) -> Plugin:
        saved = super().save(row, actor)
        self.live = None
        return saved

    def delete(self, row: Plugin, actor: Actor) -> None:
        super().delete(row, actor)
        self.live = None

    def lookup(self, name: str) -> Plugin:
        return self.single(name=name)

    def hearers(self, event: str, actor: object) -> list[Plugin]:
        return [plugin for plugin in self.enabled() if event in plugin.manifest.events and actor != Actor.plugin(plugin.name)]

    def helper_hearers(self, event: str, actor: object, role: AgentRole) -> list[Plugin]:
        return [plugin for plugin in self.hearers(event, actor) if plugin.manifest.reaches_role(event, role)]

    def other_plugins(self, name: str) -> list[Plugin]:
        return [plugin for plugin in self.all() if plugin.name != name]

    def release_plugins(self) -> list[Plugin]:
        return [plugin for plugin in self.all() if not plugin.linked and plugin.release]

    def sourced_plugins(self) -> list[Plugin]:
        return [plugin for plugin in self.all() if plugin.linked or not plugin.release]

    def enabled(self) -> list[Plugin]:
        if self.live is None:
            self.live = [p for p in self.all() if p.enabled]
        return list(self.live)
