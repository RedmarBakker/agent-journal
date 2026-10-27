from journal.engine.job import Job
from journal.features.plugins.support.plugin_faults import PluginFaults
from journal.features.plugins.support.plugin_health import HEALTH_WINDOW_SECONDS, PluginHealth
from journal.features.plugins.support.plugin_services import PluginServices
from journal.models.environment import Environment
from journal.models.plugin import Plugin
from journal.repositories.environments import Environments
from journal.repositories.plugins import Plugins
from journal.supervisor_link import SupervisorLink

HEALTH_EVENT_NAME = "health"


class PluginHealthCheck(Job):
    """Every minute each plugin that is on and declares a health check is probed in every environment its supervisor runs: a miss is a fault, five in a row mark it broken, and its services are started again; an answer clears the run of faults."""

    interval_seconds = 60.0

    def __init__(self, plugins: Plugins, environments: Environments, supervisor: SupervisorLink, health: PluginHealth, faults: PluginFaults, services: PluginServices) -> None:
        self.plugins, self.environments, self.supervisor = plugins, environments, supervisor
        self.health, self.faults, self.services = health, faults, services

    def tick(self, time: float) -> None:
        for plugin in self.plugins.enabled():
            if plugin.manifest.health.is_declared:
                self.checked(plugin)

    def checked(self, plugin: Plugin) -> None:
        missed = [environment for environment in self.supervisor.running(self.environments.all()) if not self.answered(plugin, environment)]
        if missed:
            self.services.stop(plugin)
            self.services.start(plugin)

    def answered(self, plugin: Plugin, environment: Environment) -> bool:
        silent = [probe.service for probe in self.health.probe(plugin, environment.name) if not probe.answered]
        if silent:
            self.faults.failed(plugin, environment.row_id, HEALTH_EVENT_NAME, f"{', '.join(silent)} did not answer the health check within {HEALTH_WINDOW_SECONDS * 1000:.0f} ms, so its services were started again")
            return False
        self.faults.answered(plugin, environment.row_id)
        return True
