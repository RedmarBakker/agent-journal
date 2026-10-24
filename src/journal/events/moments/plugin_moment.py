from dataclasses import dataclass

from journal.events.event import Event


@dataclass(frozen=True, kw_only=True)
class PluginMoment(Event):
    """Something that happened to a plugin, in the environment whose chat shows it."""

    environment_id: int
    plugin: str
