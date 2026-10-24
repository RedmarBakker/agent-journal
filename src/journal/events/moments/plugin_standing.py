from dataclasses import dataclass

from journal.events.moments.plugin_moment import PluginMoment


@dataclass(frozen=True, kw_only=True)
class PluginStanding(PluginMoment):
    """A change in how a plugin stands: failing, answering again, switched off, a manifest waiting, upgraded or not."""
