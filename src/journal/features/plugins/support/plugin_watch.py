import json

from journal.features.plugins.support.manifest_reader import MANIFEST
from journal.features.plugins.support.plugin_folders import PluginFolders
from journal.models.plugin import Plugin


class PluginWatch:
    """What is wrong with a plugin that was on: its manifest does not parse, its last hook or queue file failed, or it is off though nobody switched it off; empty while it works or was switched off on purpose."""

    def __init__(self, folders: PluginFolders) -> None:
        self.folders = folders

    def fault(self, plugin: Plugin) -> str:
        if not plugin.enabled:
            return "" if plugin.off_on_purpose else f"it is off, though nobody switched it off{self.last(plugin)}"
        return self.manifest_fault(plugin) or (plugin.last_fault if plugin.fault_streak else "")

    def manifest_fault(self, plugin: Plugin) -> str:
        file = self.folders.folder(plugin) / MANIFEST
        try:
            json.loads(file.read_text())
        except (OSError, ValueError) as refused:
            return f"its manifest does not parse: {refused}"
        return ""

    @staticmethod
    def last(plugin: Plugin) -> str:
        return f"; its last fault: {plugin.last_fault}" if plugin.last_fault else ""
