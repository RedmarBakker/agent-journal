from typing import ClassVar

from journal.helpers.main_role import MainRole
from journal.support.agent_role import AgentRole


class PluginRole(MainRole):
    """A plugin's program at the console: it runs what the main agent runs and, alone, its own dashboard's verbs."""

    role: ClassVar[AgentRole] = AgentRole.PLUGIN
