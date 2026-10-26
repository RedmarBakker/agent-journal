from datetime import datetime, timezone

from journal.events.announcer import Announcer
from journal.events.moments.plugin_recovered import PluginRecovered
from journal.events.moments.plugin_failing import PluginFailing
from journal.support.actor import Actor
from journal.models.entry import Entry
from journal.models.plugin import Plugin
from journal.repositories.entries import Entries
from journal.repositories.plugins import Plugins
from journal.support.time_source import TimeSource

FAULT = "plugin_fault"
FAILURE_COUNT = 5


class PluginFaults:
    """A plugin's fault lets the event through and is recorded: an entry naming the plugin, the event and the words, the row's last fault, and a card at the fifth in a row; a card again once it answers."""

    def __init__(self, plugins: Plugins, entries: Entries, announcer: Announcer, time_source: TimeSource) -> None:
        self.time_source = time_source
        self.plugins, self.entries, self.announcer = plugins, entries, announcer

    def failed(self, plugin: Plugin, environment_id: int, event: str, text: str) -> None:
        self.entries.save(Entry(environment_id=environment_id, kind=FAULT, actor=Actor.plugin(plugin.name), data={"plugin": plugin.name, "event": event, "fault": text}), Actor.system())
        row = self.plugins.lookup(plugin.name)
        failing = row.fault_streak + 1 >= FAILURE_COUNT and row.failed_at is None
        self.plugins.save(row.with_(last_fault=text, fault_streak=row.fault_streak + 1, failed_at=self.time_source.moment() if failing else row.failed_at), Actor.system())
        if failing:
            self.announcer.announce(PluginFailing(environment_id=environment_id, plugin=plugin.name, fault=text, failures=FAILURE_COUNT))

    def answered(self, plugin: Plugin, environment_id: int) -> None:
        row = self.plugins.lookup(plugin.name)
        if not row.fault_streak:
            return
        self.plugins.save(row.with_(fault_streak=0, failed_at=None), Actor.system())
        if row.failed_at is not None:
            self.announcer.announce(PluginRecovered(environment_id=environment_id, plugin=plugin.name))
