import socket
import time

from journal.features.plugins.support.plugin_folders import PluginFolders
from journal.features.plugins.support.service_health import ServiceHealth
from journal.models.plugin import Plugin
from journal.support.plugin_service import PluginService

HEALTH_WINDOW_SECONDS = 0.2


class PluginHealth:
    """A plugin's health check in one environment: each service with a health socket there is sent the plugin's request on it and answers within 200 ms or not; a service with no socket is not running there and is not asked."""

    def __init__(self, folders: PluginFolders) -> None:
        self.folders = folders

    def probe(self, plugin: Plugin, environment: str) -> list[ServiceHealth]:
        return [self.service_probe(plugin, environment, service) for service in plugin.manifest.services if self.folders.health_socket(plugin, environment, service).is_socket()]

    def service_probe(self, plugin: Plugin, environment: str, service: PluginService) -> ServiceHealth:
        began = time.monotonic()
        answered = plugin.manifest.health.is_answer(self.answer_line(self.folders.health_socket(plugin, environment, service).as_posix(), plugin.manifest.health.request))
        return ServiceHealth(service.name, answered and time.monotonic() - began <= HEALTH_WINDOW_SECONDS, time.monotonic() - began)

    @staticmethod
    def answer_line(path: str, request: str) -> str:
        with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as link:
            link.settimeout(HEALTH_WINDOW_SECONDS)
            try:
                link.connect(path)
                link.sendall((request + "\n").encode())
                return link.makefile("rb").readline().decode()
            except OSError:
                return ""
