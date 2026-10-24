import hashlib
from pathlib import Path

from journal.features.plugins.support.plugin_folders import PluginFolders
from journal.models.support.plugin_manifest import PluginManifest


class PluginHashes:
    """The hash of each file a plugin runs, taken when you install, upgrade or switch it on, so an upgrade can show what changed; the journal never switches a plugin off by itself."""

    def __init__(self, folders: PluginFolders) -> None:
        self.folders = folders
        self.checked: dict[Path, tuple[int, int, str]] = {}

    def digest(self, folder: Path, manifest: PluginManifest) -> dict[str, str]:
        return {path: self.hashed(folder / path) for path in manifest.programs}

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
