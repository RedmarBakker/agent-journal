from journal.engine.nudge import Nudge
from journal.support.timeout import Timeout


class PluginsNudges:
    """The nudges of the plugins feature."""

    PLUGIN_FILE_OWNERSHIP = Nudge("plugins", "plugin_files_are_the_users", "an installed plugin's files are the user's to change", "propose the change, or work in the plugin's own folder", repeat=Timeout.seconds(0))
