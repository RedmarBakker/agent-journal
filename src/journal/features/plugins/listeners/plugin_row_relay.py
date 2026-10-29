from functools import partial
from journal.db.commit_queue import CommitQueue
from journal.events.agent.file_edited import FileEdited
from journal.events.models.created import Created
from journal.events.models.model_event import ModelEvent
from journal.events.listener import Listener
from journal.models.edit import Edit
from journal.features.plugins.support.plugin_relay import PluginRelay
from journal.support.listener_queue import ListenerQueue
from journal.repositories.agents import Agents
from journal.repositories.scope import Scope


class PluginRowRelay(Listener[ModelEvent]):
    """The plugins that receive a row's change receive it after the write commits and after the reply, so none blocks the database, receives a rolled-back row or stops the save."""

    def __init__(self, relay: PluginRelay, deferred: ListenerQueue, commits: CommitQueue, scope: Scope, agents: Agents) -> None:
        self.relay, self.deferred, self.commits, self.scope, self.agents = relay, deferred, commits, scope, agents

    def handle(self, event: ModelEvent) -> None:
        environment_id = self.scope.id_default(0)
        notified = self.notified(event)
        for plugin in self.relay.listeners(notified, environment_id):
            if plugin.manifest.has_window(notified.key):
                continue
            self.commits.add(partial(self.deferred.add_bounded, partial(self.relay.postponed, plugin, notified, environment_id), f"{plugin.name} relay {notified.key}"))

    def notified(self, event: ModelEvent) -> ModelEvent | FileEdited:
        if not isinstance(event, Created) or not isinstance(event.model, Edit):
            return event
        editors = self.agents.session_rows(event.model.session)
        return FileEdited.build(event.model, editors[0]) if editors else event
