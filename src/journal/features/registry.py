from journal.support.card_family import CardFamily
from journal.support.mark_kind import MarkKind
from journal.support.mark_kinds import MarkKinds
from journal.engine.support.modes import Modes
from journal.support.agent_role import AgentRole
from journal.engine.base_state import BaseState
from journal.engine.conduct import Conduct
from journal.engine.safety_conduct import SafetyConduct
from journal.engine.demand_conduct import DemandConduct
from journal.engine.demand import Demand
from journal.console.command import Command
from journal.features.double_registration import DoubleRegistration
from journal.features.feature import Feature
from journal.features.helper_files_invalid import HelperFilesInvalid
from journal.features.helper import Helper
from journal.engine.nudge import Nudge
from journal.features.support.service import Service
from journal.support.skill import Skill
from journal.repositories.setting_rows import SettingRows


ENGINE = "engine"


class Registry:
    """Every feature, and whether each is on in an environment, and every helper's file, which alone says what reaches that helper; what the journal demands of an agent is the main agent's alone. The catalogue, the bus and the console are filled from here at boot."""

    def __init__(self, features: tuple[type[Feature], ...], settings: SettingRows, standard_commands: tuple[type[Command], ...] = (), helpers: tuple[type[Helper], ...] = ()) -> None:
        self.features, self.settings, self.standard_commands = features, settings, standard_commands
        self._by_name = {feature.name: feature for feature in features}
        self._by_state = {state.name: feature for feature in features for state in feature.states}
        self._feature_names = self.feature_names(features)
        self._helpers = self.helper_files(helpers)

    @staticmethod
    def feature_names(features: tuple[type[Feature], ...]) -> dict[type, str]:
        names: dict[type, str] = {}
        for feature in features:
            for registered in Registry.registered_classes(feature):
                if registered in names:
                    raise DoubleRegistration(f"{registered.__name__} is registered by the features {names[registered]} and {feature.name}")
                names[registered] = feature.name
        return names

    @staticmethod
    def registered_classes(feature: type[Feature]) -> set[type]:
        helper_conducts = {conduct for conducts in feature.helper_conduct.values() for conduct in conducts}
        return {*feature.listeners, *feature.conduct, *helper_conducts, *feature.commands, *feature.states, *feature.jobs, *feature.seeds, *feature.process_cards, *feature.host_writers}

    def helper_files(self, helpers: tuple[type[Helper], ...]) -> dict[AgentRole, type[Helper]]:
        for role in AgentRole.helpers():
            files = [helper.__name__ for helper in helpers if helper.role == role]
            if len(files) != 1:
                raise HelperFilesInvalid(f"the helper role {role.value} has {len(files)} files ({', '.join(files) or 'none'}): each helper role has exactly one")
        for helper in helpers:
            redundant = [listed.__name__ for listed in helper.listeners if self.gives_helper(listed, self.owning_feature(listed), helper)]
            if redundant:
                raise HelperFilesInvalid(f"{helper.__name__} names {', '.join(redundant)} alone, but a feature in its features already gives it to the {helper.role.value}")
        return {helper.role: helper for helper in helpers}

    def helper(self, role: AgentRole) -> type[Helper]:
        return self._helpers[role]

    def reaches_helper(self, registered: type, role: AgentRole) -> bool:
        feature_name, helper = self.owning_feature(registered), self.helper(role)
        return feature_name == ENGINE or registered in helper.listeners or self.gives_helper(registered, feature_name, helper)

    def gives_helper(self, registered: type, feature_name: str, helper: type[Helper]) -> bool:
        return feature_name in helper.feature_names() and registered in self._by_name[feature_name].helper_listeners.get(helper.role, ())

    def refused_parts(self, role: AgentRole) -> frozenset[str]:
        if not role.is_helper():
            return frozenset()
        allowed = self.helper(role).feature_names()
        return frozenset(name for feature in self.features if feature.name not in allowed for name in feature.part_names())

    def receives_row_event(self, feature_name: str, role: AgentRole) -> bool:
        return not role.is_helper() or feature_name == ENGINE or feature_name in self.helper(role).feature_names()

    def helper_features(self, role: AgentRole) -> frozenset[str]:
        return self.helper(role).feature_names()

    def runs_verb(self, command: type[Command], verb: str, role: AgentRole) -> bool:
        return not role.is_helper() or self.helper(role).runs(command, verb)

    def helper_file(self, role: AgentRole) -> str:
        return self.helper(role).__name__

    def helper_verbs(self, role: AgentRole) -> tuple[str, ...]:
        return tuple(f"journal {command.noun} {verb}" for command, verb in self.helper(role).commands)

    def roles(self) -> tuple[AgentRole, ...]:
        return (AgentRole.MAIN, *self._helpers)

    def owning_feature(self, registered: type) -> str:
        return self._feature_names.get(registered, ENGINE)

    def has_feature(self, name: str) -> bool:
        return name in self._by_name

    def is_enabled(self, feature: type[Feature]) -> bool:
        return feature.fixed or bool(self.settings.get(f"features.{feature.name}", feature.default))

    def required_skill(self, state: str) -> Skill | None:
        return next((skill for skill in self.skills() if state in skill.required_states), None)

    def options(self) -> list:
        return [option for feature in self.features for option in feature.options]

    def conducts(self, role: AgentRole) -> tuple[type[Conduct], ...]:
        if role.is_helper():
            return (SafetyConduct, DemandConduct, *(conduct for feature in self.helper(role).features for conduct in feature.helper_conduct.get(role, ())))
        return (SafetyConduct, DemandConduct, *(conduct for feature in self.features for conduct in feature.conduct))

    def demands(self, role: AgentRole) -> tuple[Demand, ...]:
        if role.is_helper():
            return ()
        return tuple(demand for feature in self.features for demand in feature.demands)

    def states(self) -> list[type[BaseState]]:
        return [state for feature in self.features for state in feature.states]

    def modes(self) -> list[Modes]:
        return [feature.modes for feature in self.features if feature.modes]

    def floors(self) -> dict[AgentRole, type[BaseState]]:
        return {role: helper.first_state for role, helper in self._helpers.items()}

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
