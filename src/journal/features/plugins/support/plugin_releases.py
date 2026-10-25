import subprocess
from pathlib import Path

from journal.events.announcer import Announcer
from journal.events.moments.plugin_upgrade_failed import PluginUpgradeFailed
from journal.events.moments.plugin_upgraded import PluginUpgraded
from journal.features.plugins.support.plugin_installing import PluginInstalling
from journal.features.plugins.support.plugin_tags import PluginTags
from journal.support.release import Release
from journal.models.plugin import Plugin
from journal.repositories.environments import Environments
from journal.repositories.plugins import Plugins
from journal.support.actor import Actor
from journal.support.rejection import Rejection

GIT_SECONDS = 120


class PluginReleases:
    """The installed plugins updated to the journal's version: each one installed from a release moves to its newest release whose manifest's journal field, the lowest journal version it runs on, the running journal satisfies; one installed from a folder or a branch moves to the newest release tag of its source, among the fifty nearest above its version, that runs on it, a folder with uncommitted changes being left as it is and named; and the chat is given what moved."""

    def __init__(self, plugins: Plugins, installing: PluginInstalling, tags: PluginTags, announcer: Announcer, environments: Environments) -> None:
        self.plugins, self.installing, self.tags, self.announcer, self.environments = plugins, installing, tags, announcer, environments

    def upgraded_all(self, version: str, actor: Actor) -> None:
        for plugin in self.plugins.release_plugins():
            self.upgraded(plugin, version, actor)
        for plugin in self.plugins.sourced_plugins():
            self.source_upgraded(plugin, version, actor)

    def upgraded(self, plugin: Plugin, version: str, actor: Actor) -> None:
        self.moved(plugin, version, actor, self.newer(plugin.source, Release(plugin.release)), Release(plugin.release).tag)

    def source_upgraded(self, plugin: Plugin, version: str, actor: Actor) -> None:
        try:
            current = Release(plugin.manifest.version)
            current.numbers
        except ValueError:
            return
        if plugin.linked and self.has_changes(Path(plugin.source)):
            self.announcer.announce(PluginUpgradeFailed(environment_id=self.environments.all()[0].row_id, plugin=plugin.name, version=version, reason=f"its folder {plugin.source} has changes not committed, so it was left as it is"))
            return
        self.moved(plugin, version, actor, self.newer(plugin.source, current), plugin.manifest.version)

    def newer(self, source: str, current: Release) -> list[Release]:
        try:
            return self.tags.newer(source, current)
        except OSError:
            return []

    @staticmethod
    def has_changes(folder: Path) -> bool:
        return bool(subprocess.run(["git", "-C", str(folder), "status", "--porcelain"], capture_output=True, text=True, timeout=GIT_SECONDS).stdout.strip())

    def moved(self, plugin: Plugin, version: str, actor: Actor, newer: list[Release], previous: str) -> None:
        environment = self.environments.all()[0]
        try:
            tag = self.fitting_tag(plugin, newer, Release(version))
            if tag is None:
                self.record_wait(plugin, newer)
                return
            if plugin.linked:
                subprocess.run(["git", "-C", plugin.source, "checkout", "--quiet", tag], capture_output=True, text=True, timeout=GIT_SECONDS)
            self.installing.upgrade(plugin.name, tag, environment.name, actor)
        except (OSError, Rejection) as failed:
            self.announcer.announce(PluginUpgradeFailed(environment_id=environment.row_id, plugin=plugin.name, version=version, reason=str(failed)))
            return
        self.announcer.announce(PluginUpgraded(environment_id=environment.row_id, plugin=plugin.name, previous=previous, tag=tag, version=version))

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
