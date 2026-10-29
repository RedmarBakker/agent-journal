from typing import ClassVar

from journal.console.command import Command
from journal.engine.base_state import BaseState
from journal.engine.conduct import Conduct
from journal.engine.demand import Demand
from journal.engine.demand_conduct import DemandConduct
from journal.engine.safety_conduct import SafetyConduct
from journal.features.feature import Feature
from journal.features.role import Role
from journal.models.support.plugin_manifest import PluginManifest
from journal.support.agent_role import AgentRole
from journal.models.alias import Alias

class MainRole(Role):
    """The main agent's role: every feature's conduct, mode conduct and demands reach it, every listener hears it, no part is refused it and it runs every verb."""

    role: ClassVar[AgentRole] = AgentRole.MAIN

    @classmethod
    def conducts(cls, features: tuple[type[Feature], ...]) -> tuple[type[Conduct], ...]:
        return (SafetyConduct, DemandConduct, *(conduct for feature in features for conduct in feature.conduct))

    @classmethod
    def mode_conducts(cls, features: tuple[type[Feature], ...], lowest_state: type[BaseState]) -> tuple[type[Conduct], ...]:
        return tuple(conduct for feature in features for mode_state, conduct in feature.mode_conduct if lowest_state is mode_state)

    @classmethod
    def demands(cls, features: tuple[type[Feature], ...]) -> tuple[Demand, ...]:
        return tuple(demand for feature in features for demand in feature.demands)

    @classmethod
    def reaches(cls, registered: type, owner_name: str, feature_catalogue: dict[str, type[Feature]]) -> bool:
        return True

    @classmethod
    def refused_parts(cls, features: tuple[type[Feature], ...]) -> frozenset[str]:
        return frozenset(name for feature in features for name in feature.helper_part_names())

    @classmethod
    def receives_row_event(cls, feature_name: str) -> bool:
        return True

    @classmethod
    def runs(cls, command: type[Command], verb: str) -> bool:
        return True

    @classmethod
    def reaches_plugin(cls, manifest: PluginManifest, key: str) -> bool:
        return True

    @classmethod
    def takes_plugin_lines(cls) -> bool:
        return True

    @classmethod
    def runs_alias(cls, alias: Alias) -> bool:
        return True

    @classmethod
    def has_transcript(cls) -> bool:
        return True

    @classmethod
    def has_researchers(cls) -> bool:
        return True
