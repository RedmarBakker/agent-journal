import hashlib
import json

from journal.events.announcer import Announcer
from journal.events.moments.plugin_manifest_changed import PluginManifestChanged
from journal.features.plugins.support.manifest_reader import MANIFEST, ManifestReader
from journal.features.plugins.support.plugin_changes import PluginChanges
from journal.features.plugins.support.plugin_folders import PluginFolders
from journal.support.actor import Actor
from journal.models.plugin import Plugin
from journal.support.rejection import Rejection
from journal.repositories.plugins import Plugins


class LinkedManifests:
    """A linked folder's manifest changed since the user last read it: the plugin goes on as it was installed, and a card shows the change once, until the user applies it with an upgrade."""

    def __init__(self, folders: PluginFolders, plugins: Plugins, announcer: Announcer, reader: ManifestReader) -> None:
        self.folders, self.plugins, self.announcer, self.reader = folders, plugins, announcer, reader

    def notice(self, plugin: Plugin, environment_id: int) -> None:
        if not plugin.linked:
            return
        file = self.folders.folder(plugin) / MANIFEST
        text = file.read_text() if file.is_file() else ""
        viewed = hashlib.sha256(text.encode()).hexdigest()
        if viewed == plugin.waiting:
            return
        try:
            changes = PluginChanges.manifest(PluginChanges.plain(plugin.manifest), PluginChanges.plain(self.reader.read(self.folders.folder(plugin))))
        except (Rejection, json.JSONDecodeError) as refused:
            changes = [f"the manifest is refused: {refused}"]
        if not changes:
            return
        self.plugins.save(plugin.with_(waiting=viewed), Actor.system())
        self.announcer.announce(PluginManifestChanged(environment_id=environment_id, plugin=plugin.name, changes="\n".join(changes)))
