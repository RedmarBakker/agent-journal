from journal.features.plugins.support.plugin_services import PluginServices
from journal.features.seed import Seed
from journal.repositories.plugins import Plugins


class PluginServicesSeed(Seed):
    """At boot, the services of every plugin that is on are started fresh where a supervisor runs: one still running from before is ended first."""

    def __init__(self, plugins: Plugins, services: PluginServices) -> None:
        self.plugins, self.services = plugins, services

    def run(self) -> None:
        for plugin in self.plugins.enabled():
            self.services.stop(plugin)
            self.services.start(plugin)
