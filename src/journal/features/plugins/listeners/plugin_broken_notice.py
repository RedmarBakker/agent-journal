from journal.engine.support.nudge_log import NudgeLog
from journal.events.agent.ticked import Ticked
from journal.events.agent_listener import AgentListener
from journal.features.plugins.plugins_nudges import PluginsNudges
from journal.features.plugins.support.plugin_watch import PluginWatch
from journal.repositories.plugins import Plugins


class PluginBrokenNotice(AgentListener[Ticked]):
    """A plugin that was on and no longer works is named to the agent with its fault, again every five minutes, until it works or is switched off on purpose."""

    def __init__(self, plugins: Plugins, watch: PluginWatch, nudges: NudgeLog) -> None:
        self.plugins, self.watch, self.nudges = plugins, watch, nudges

    def handle(self, event: Ticked) -> None:
        for plugin in self.plugins.all():
            fault = self.watch.fault(plugin)
            if fault:
                self.nudges.type(PluginsNudges.PLUGIN_BROKEN.create(plugin=plugin.name, fault=fault))
