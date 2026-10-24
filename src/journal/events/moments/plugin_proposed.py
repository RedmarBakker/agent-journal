from dataclasses import dataclass

from journal.events.moments.plugin_moment import PluginMoment
from journal.support.actor import Actor


@dataclass(frozen=True, kw_only=True)
class PluginProposed(PluginMoment):
    """The agent proposed a plugin to the user, with why, what it is and the command that installs it."""

    explanation: str
    detail: str
    command: str
    actor: Actor
