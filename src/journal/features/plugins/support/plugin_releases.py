from journal.events.announcer import Announcer
from journal.events.moments.plugin_upgrade_failed import PluginUpgradeFailed
from journal.events.moments.plugin_upgraded import PluginUpgraded
from journal.features.plugins.support.plugin_installing import PluginInstalling
from journal.support.release import Release
from journal.features.updates.support.release_source import ReleaseSource
from journal.models.plugin import Plugin
from journal.repositories.environments import Environments
from journal.repositories.plugins import Plugins
from journal.support.actor import Actor
from journal.support.rejection import Rejection


class PluginReleases:
    """The installed plugins updated to the journal's version: each one installed from a source moves to its newest release whose manifest's journal field, the lowest journal version it runs on, the running journal satisfies, and the chat is given what moved."""

    def __init__(self, plugins: Plugins, installing: PluginInstalling, source: ReleaseSource, announcer: Announcer, environments: Environments) -> None:
        self.plugins, self.installing, self.source, self.announcer, self.environments = plugins, installing, source, announcer, environments

    def upgraded_all(self, version: str, actor: Actor) -> None:
        for plugin in self.plugins.release_plugins():
            self.upgraded(plugin, version, actor)

    def upgraded(self, plugin: Plugin, version: str, actor: Actor) -> None:
        try:
            tag = self.fitting_tag(plugin, Release(version))
            if tag is None:
                return
            environment = self.environments.all()[0]
            self.installing.upgrade(plugin.name, tag, environment.name, actor)
        except (OSError, Rejection) as failed:
            self.announcer.announce(PluginUpgradeFailed(environment_id=self.environments.all()[0].row_id, plugin=plugin.name, version=version, reason=str(failed)))
            return
        self.announcer.announce(PluginUpgraded(environment_id=environment.row_id, plugin=plugin.name, previous=plugin.release, tag=tag, version=version))

    def fitting_tag(self, plugin: Plugin, journal: Release) -> str | None:
        newer = [release for release in reversed(Release.lookup(self.source.release_tags(plugin.source))) if release.is_newer(Release(plugin.release))]
        return next((release.tag for release in newer if self.is_compatible(plugin, release.tag, journal)), None)

    def is_compatible(self, plugin: Plugin, tag: str, journal: Release) -> bool:
        with self.installing.staged(plugin.source, tag) as (folder, _):
            least = self.installing.reader.least_journal(folder)
        return not least or not Release(least).is_newer(journal)
