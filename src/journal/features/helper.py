from typing import ClassVar

from journal.console.command import Command
from journal.engine.base_state import BaseState
from journal.engine.conduct import Conduct
from journal.engine.demand import Demand
from journal.engine.demand_conduct import DemandConduct
from journal.engine.safety_conduct import SafetyConduct
from journal.engine.states.void import Void
from journal.events.listener import Listener
from journal.features.feature import Feature
from journal.features.role import ENGINE, Role
from journal.models.support.plugin_manifest import PluginManifest
from journal.support.agent_role import AgentRole
from journal.models.alias import Alias
from journal.features.aliases.support.plain_alias_line import PlainAliasLine

class Helper(Role):
    """What one helper is and may do, said in its own file alone: its role, the state its stack starts with over Void, the features turned on whole for it (the conduct, listeners and data each gives its role), the listeners turned on alone, and the command verbs it runs, each command once with its verbs; nothing else of the journal reaches it."""

    role: ClassVar[AgentRole]
    first_state: ClassVar[type[BaseState]] = Void
    features: ClassVar[tuple[type[Feature], ...]] = ()
    commands: ClassVar[tuple[tuple[type[Command], tuple[str, ...]], ...]] = ()
    listeners: ClassVar[tuple[type[Listener], ...]] = ()

    @classmethod
    def feature_names(cls) -> frozenset[str]:
        return frozenset(feature.name for feature in cls.features)

    @classmethod
    def runs(cls, command: type[Command], verb: str) -> bool:
        return any(listed is command and verb in verbs for listed, verbs in cls.commands)

    @classmethod
    def conducts(cls, features: tuple[type[Feature], ...]) -> tuple[type[Conduct], ...]:
        return (SafetyConduct, DemandConduct, *(conduct for feature in cls.features for conduct in feature.helper_conduct.get(cls.role, ())))

    @classmethod
    def floor_conducts(cls, features: tuple[type[Feature], ...], lowest_state: type[BaseState]) -> tuple[type[Conduct], ...]:
        return ()

    @classmethod
    def demands(cls, features: tuple[type[Feature], ...]) -> tuple[Demand, ...]:
        return ()

    @classmethod
    def reaches(cls, registered: type, owner_name: str, feature_catalogue: dict[str, type[Feature]]) -> bool:
        return owner_name == ENGINE or registered in cls.listeners or cls.gives(registered, owner_name, feature_catalogue)

    @classmethod
    def gives(cls, registered: type, owner_name: str, feature_catalogue: dict[str, type[Feature]]) -> bool:
        return owner_name in cls.feature_names() and registered in feature_catalogue[owner_name].helper_listeners.get(cls.role, ())

    @classmethod
    def refused_parts(cls, features: tuple[type[Feature], ...]) -> frozenset[str]:
        refused_features = frozenset(name for feature in features if feature.name not in cls.feature_names() for name in (*feature.part_names(), *feature.helper_part_names()))
        return refused_features | frozenset(name for feature in features for name in feature.helper_part_names() - feature.role_part_names(cls.role))

    @classmethod
    def receives_row_event(cls, feature_name: str) -> bool:
        return feature_name == ENGINE or feature_name in cls.feature_names()

    @classmethod
    def reaches_plugin(cls, manifest: PluginManifest, key: str) -> bool:
        return manifest.reaches_role(key, cls.role)

    @classmethod
    def takes_plugin_lines(cls) -> bool:
        return False

    @classmethod
    def runs_alias(cls, alias: Alias) -> bool:
        return True

    @classmethod
    def has_transcript(cls) -> bool:
        return False

    @classmethod
    def has_researchers(cls) -> bool:
        return False

    @classmethod
    def alias_line(cls) -> type:
        return PlainAliasLine
