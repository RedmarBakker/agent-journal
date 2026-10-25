from journal.support.card_family import CardFamily
from journal.support.mark_kind import MarkKind
from journal.support.mark_kinds import MarkKinds
from journal.engine.support.modes import Modes
from journal.models.agent_role import AgentRole
from journal.engine.base_state import BaseState
from journal.engine.conduct import Conduct
from journal.engine.safety_conduct import SafetyConduct
from journal.engine.demand_conduct import DemandConduct
from journal.engine.demand import Demand
from journal.console.command import Command
from journal.features.feature import Feature
from journal.engine.nudge import Nudge
from journal.features.support.service import Service
from journal.support.skill import Skill
from journal.repositories.setting_rows import SettingRows


ROLE_CONDUCT = {AgentRole.MAIN: lambda feature: feature.conduct, AgentRole.WORKER: lambda feature: feature.worker_conduct, AgentRole.VERIFIER: lambda feature: (), AgentRole.REVIEWER: lambda feature: ()}
# what the journal demands of an agent is the main agent's: the user's messages, the skills and the marks are its, and a worker owes none of them
ROLE_DEMANDS = {AgentRole.MAIN: lambda feature: feature.demands, AgentRole.WORKER: lambda feature: (), AgentRole.VERIFIER: lambda feature: (), AgentRole.REVIEWER: lambda feature: ()}


class Registry:
    """Every feature, and whether each is on in an environment. The catalogue, the bus and the console are filled from here at boot."""

    def __init__(self, features: tuple[type[Feature], ...], settings: SettingRows, standard_commands: tuple[type[Command], ...] = ()) -> None:
        self.features, self.settings, self.standard_commands = features, settings, standard_commands
        self._by_name = {feature.name: feature for feature in features}
        self._by_state = {state.name: feature for feature in features for state in feature.states}

    def has_feature(self, name: str) -> bool:
        return name in self._by_name

    def is_enabled(self, feature: type[Feature]) -> bool:
        return feature.fixed or bool(self.settings.get(f"features.{feature.name}", feature.default))

    def required_skill(self, state: str) -> Skill | None:
        return next((skill for skill in self.skills() if state in skill.required_states), None)

    def options(self) -> list:
        return [option for feature in self.features for option in feature.options]

    def conducts(self, role: AgentRole) -> tuple[type[Conduct], ...]:
        return (SafetyConduct, DemandConduct, *(conduct for feature in self.features for conduct in ROLE_CONDUCT[role](feature)))

    def demands(self, role: AgentRole) -> tuple[Demand, ...]:
        return tuple(demand for feature in self.features for demand in ROLE_DEMANDS[role](feature))

    def states(self) -> list[type[BaseState]]:
        return [state for feature in self.features for state in feature.states]

    def modes(self) -> list[Modes]:
        return [feature.modes for feature in self.features if feature.modes]

    def floors(self) -> dict[AgentRole, type[BaseState]]:
        return {role: state for feature in self.features for role, state in feature.floors.items()}

    def services(self) -> list[Service]:
        return [service for feature in self.features for service in feature.services]

    def is_background_verb(self, noun: str, verb: str) -> bool:
        return any(command.noun == noun and verb in command.background_verbs for feature in self.features for command in feature.commands)

    def uncut_verbs(self) -> tuple[str, ...]:
        commands = [*self.standard_commands, *(command for feature in self.features for command in feature.commands)]
        return tuple(f"{command.noun} {verb}" for command in commands for verb in sorted(command.uncut_verbs))

    def card_families(self) -> list[CardFamily]:
        return [*MarkKinds.FAMILIES, *(family for feature in self.features for family in feature.card_families)]

    def card_kinds(self) -> list[MarkKind]:
        return [*MarkKinds.KINDS, *(kind for feature in self.features for kind in feature.card_kinds)]

    def skills(self) -> list[Skill]:
        return [feature.skill for feature in self.features if feature.skill]

    def skill(self, name: str) -> Skill | None:
        return next((skill for skill in self.skills() if skill.name == name), None)

    def nudge_keyed(self, key: str) -> Nudge | None:
        return next((nudge for feature in self.features for nudge in feature.nudges if nudge.key == key), None)

    def owner(self, nudge: Nudge) -> type[Feature]:
        return self._by_name[nudge.feature]

    def silenced(self, nudge: Nudge) -> bool:
        return nudge.feature in self._by_name and not self.is_enabled(self.owner(nudge))
