import time

from journal.features.plugins.support.plugin_folders import PluginFolders
from journal.features.plugins.support.plugin_runner import PluginRunner
from journal.features.plugins.support.protocol import Protocol
from journal.models.plugin import Plugin
from journal.features.plugins.support.plugin_fault import PluginFault

HEALTH_WINDOW_SECONDS = 0.2


class PluginHealth:
    """A plugin's health probe: the health event sent to its service's socket in one environment, answered within 200 ms or not responding, with how long the answer took; its program never stands in for the service."""

    def __init__(self, runner: PluginRunner, protocol: Protocol, folders: PluginFolders) -> None:
        self.runner, self.protocol, self.folders = runner, protocol, folders

    def probe(self, plugin: Plugin, environment: str) -> float | None:
        began = time.monotonic()
        try:
            self.runner.service_run(self.folders.socket(plugin, environment), self.protocol.health_line(environment), HEALTH_WINDOW_SECONDS)
        except (PluginFault, OSError):
            return None
        return time.monotonic() - began
