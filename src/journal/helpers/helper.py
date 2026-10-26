from typing import ClassVar

from journal.console.command import Command
from journal.engine.base_state import BaseState
from journal.engine.states.void import Void
from journal.events.listener import Listener
from journal.features.feature import Feature
from journal.models.agent_role import AgentRole


class Helper:
    """What one helper is and may do, said in its own file alone: its role, the state its stack starts with over Void, the features turned on whole for it (the conduct, listeners and data each gives its role), the listeners turned on alone, and the command verbs it runs, each a command and one of its verbs; nothing else of the journal reaches it."""

    role: ClassVar[AgentRole]
    first_state: ClassVar[type[BaseState]] = Void
    features: ClassVar[tuple[type[Feature], ...]] = ()
    commands: ClassVar[tuple[tuple[type[Command], str], ...]] = ()
    listeners: ClassVar[tuple[type[Listener], ...]] = ()

    @classmethod
    def feature_names(cls) -> frozenset[str]:
        return frozenset(feature.name for feature in cls.features)

    @classmethod
    def runs(cls, command: type[Command], verb: str) -> bool:
        return (command, verb) in cls.commands
