from typing import ClassVar

from journal.console.command import Command
from journal.engine.base_state import BaseState
from journal.engine.conduct import Conduct
from journal.engine.demand import Demand
from journal.features.feature import Feature
from journal.models.support.plugin_manifest import PluginManifest
from journal.support.agent_role import AgentRole

ENGINE = "engine"
from journal.models.alias import Alias

class Role:
    """What reaches the agents of one role and what they may run, said in that role's own file: the main agent's or a helper's."""

    role: ClassVar[AgentRole]

    @classmethod
    def conducts(cls, features: tuple[type[Feature], ...]) -> tuple[type[Conduct], ...]:
        raise NotImplementedError

    @classmethod
    def mode_conducts(cls, features: tuple[type[Feature], ...], lowest_state: type[BaseState]) -> tuple[type[Conduct], ...]:
        raise NotImplementedError

    @classmethod
    def demands(cls, features: tuple[type[Feature], ...]) -> tuple[Demand, ...]:
        raise NotImplementedError

    @classmethod
    def reaches(cls, registered: type, owner_name: str, feature_catalogue: dict[str, type[Feature]]) -> bool:
        raise NotImplementedError

    @classmethod
    def refused_parts(cls, features: tuple[type[Feature], ...]) -> frozenset[str]:
        raise NotImplementedError

    @classmethod
    def receives_row_event(cls, feature_name: str) -> bool:
        raise NotImplementedError

    @classmethod
    def runs(cls, command: type[Command], verb: str) -> bool:
        raise NotImplementedError

    @classmethod
    def reaches_plugin(cls, manifest: PluginManifest, key: str) -> bool:
        raise NotImplementedError

    @classmethod
    def takes_plugin_lines(cls) -> bool:
        raise NotImplementedError

    @classmethod
    def runs_alias(cls, alias: Alias) -> bool:
        raise NotImplementedError

    @classmethod
    def has_transcript(cls) -> bool:
        raise NotImplementedError

    @classmethod
    def has_researchers(cls) -> bool:
        raise NotImplementedError
