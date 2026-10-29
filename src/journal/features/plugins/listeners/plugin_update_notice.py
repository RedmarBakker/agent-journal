from journal.events.journal_updated import JournalUpdated
from journal.events.listener import Listener
from journal.features.plugins.support.plugin_releases import PluginReleases
from journal.support.listener_queue import ListenerQueue


class PluginUpdateNotice(Listener[JournalUpdated]):
    """Once the journal has been updated, every plugin with a newer release that runs on the new journal is offered its update, after the boot and off any request; nothing is installed until the user presses Install."""

    def __init__(self, releases: PluginReleases, deferred: ListenerQueue) -> None:
        self.releases, self.deferred = releases, deferred

    def handle(self, event: JournalUpdated) -> None:
        self.deferred.add(lambda: self.releases.offered_all(event.current))
