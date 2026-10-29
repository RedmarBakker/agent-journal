from typing import ClassVar

from journal.support.actor import Actor
from journal.support.actor_type import ActorType


class PluginActor(Actor):
    """A plugin's program, by the plugin's name."""

    kind: ClassVar[ActorType] = ActorType.PLUGIN
