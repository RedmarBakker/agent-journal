import hashlib
from pathlib import Path

from journal.events.announcer import Announcer
from journal.events.moments.plugin_switched_off import PluginSwitchedOff
from journal.features.plugins.support.plugin_folders import PluginFolders
from journal.models.support.plugin_manifest import PluginManifest
from journal.support.actor import Actor
from journal.models.plugin import Plugin
from journal.repositories.plugins import Plugins


class PluginHashes:
    """The hash of each file a plugin runs, taken when you install, upgrade or switch it on and checked before each run; a plugin whose files changed is switched off with a card, until you switch it on again."""

    def __init__(self, folders: PluginFolders, plugins: Plugins, announcer: Announcer) -> None:
        self.folders, self.plugins, self.announcer = folders, plugins, announcer
        self.checked: dict[Path, tuple[int, int, str]] = {}

    def digest(self, folder: Path, manifest: PluginManifest) -> dict[str, str]:
        return {path: self.hashed(folder / path) for path in manifest.programs}

    def intact(self, plugin: Plugin, environment_id: int) -> bool:
        changed = [path for path, prior_row in plugin.hashes.items() if self.hashed(self.folders.folder(plugin) / path) != prior_row]
        if not changed:
            return True
        self.plugins.save(self.plugins.lookup(plugin.name).with_(enabled=False), Actor.system())
        self.announcer.announce(PluginSwitchedOff(environment_id=environment_id, plugin=plugin.name, changed=", ".join(changed)))
        return False

    def hashed(self, path: Path) -> str:
        if not path.is_file():
            return ""
        stat = path.stat()
        record = self.checked.get(path)
        if record and record[0] == stat.st_mtime_ns and record[1] == stat.st_size:
            return record[2]
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        self.checked[path] = (stat.st_mtime_ns, stat.st_size, digest)
        return digest
