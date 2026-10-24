from journal.engine.conduct import Conduct
from journal.engine.support.settings import Settings
from journal.engine.support.transition import Transition
from journal.events.agent.tool_starting import ToolStarting
from journal.features.plugins.plugins_nudges import PluginsNudges
from journal.features.plugins.plugins_part import PluginsPart


class PluginsConduct(Conduct):
    """The plugins feature's conduct in every state: the agent never changes an installed plugin's files, so an edit or a shell line that writes into the plugins folder is blocked. Running a plugin's program is not writing to it; a linked folder is the agent's to work in."""

    def on_tool_starting(self, event: ToolStarting, settings: Settings) -> Transition:
        plugins = event.data.part(PluginsPart)
        if not event.call.is_folder_write(plugins.root, plugins.plugins_folder):
            return self.none()
        return self.refuse(PluginsNudges.PLUGIN_FILE_OWNERSHIP.create())
