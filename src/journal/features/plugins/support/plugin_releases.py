from journal.events.announcer import Announcer
from journal.events.moments.plugin_upgrade_failed import PluginUpgradeFailed
from journal.events.moments.plugin_update_available import PluginUpdateAvailable
from journal.features.plugins.support.plugin_installing import PluginInstalling
from journal.features.plugins.support.plugin_tags import PluginTags
from journal.support.release import Release
from journal.models.plugin import Plugin
from journal.repositories.environments import Environments
from journal.repositories.plugins import Plugins
from journal.support.actor import Actor
from journal.support.rejection import Rejection


class PluginReleases:
    """The plugin updates offered once the journal is updated, never installed by themselves: for each plugin installed from a release, its newest release whose manifest's journal field, the lowest journal version it runs on, the running journal satisfies; for one installed from a folder or a branch, the newest release tag of its source, among the fifty nearest above its version, that runs on it; each offered in the chat, to install only when the user presses Install in its dialog."""

    def __init__(self, plugins: Plugins, installing: PluginInstalling, tags: PluginTags, announcer: Announcer, environments: Environments) -> None:
        self.plugins, self.installing, self.tags, self.announcer, self.environments = plugins, installing, tags, announcer, environments

    def offered_all(self, version: str) -> None:
        for plugin in self.plugins.release_plugins():
            self.release_offered(plugin, version)
        for plugin in self.plugins.sourced_plugins():
            self.source_offered(plugin, version)

    def release_offered(self, plugin: Plugin, version: str) -> None:
        self.offered(plugin, version, self.newer(plugin.source, Release(plugin.release)), Release(plugin.release).tag)

    def source_offered(self, plugin: Plugin, version: str) -> None:
        try:
            current = Release(plugin.manifest.version)
            current.numbers
        except ValueError:
            return
        self.offered(plugin, version, self.newer(plugin.source, current), plugin.manifest.version)

    def newer(self, source: str, current: Release) -> list[Release]:
        try:
            return self.tags.newer(source, current)
        except OSError:
            return []

    def offered(self, plugin: Plugin, version: str, newer: list[Release], previous: str) -> None:
        environment = self.environments.all()[0]
        try:
            tag = self.fitting_tag(plugin, newer, Release(version))
            if tag is None:
                self.record_wait(plugin, newer)
                return
        except (OSError, Rejection) as failed:
            self.announcer.announce(PluginUpgradeFailed(environment_id=environment.row_id, plugin=plugin.name, version=version, reason=str(failed)))
            return
        self.announcer.announce(PluginUpdateAvailable(environment_id=environment.row_id, plugin=plugin.name, previous=previous, tag=tag))

    def record_wait(self, plugin: Plugin, newer: list[Release]) -> None:
        if not newer:
            return
        with self.installing.staged(plugin.source, newer[-1].tag) as (folder, _):
            least = self.installing.reader.least_journal(folder)
        self.plugins.save(self.plugins.lookup(plugin.name).with_(wait_target=least), Actor.system())

    def fitting_tag(self, plugin: Plugin, newer: list[Release], journal: Release) -> str | None:
        with self.installing.staged(plugin.source, "HEAD") as (folder, _):
            newest_fit = self.tags.fitting(folder, newer, journal)
        return newest_fit.tag if newest_fit is not None else None
