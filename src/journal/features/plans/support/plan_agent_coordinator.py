from journal.engine.states_catalogue import StatesCatalogue
from journal.engine.support.settings import Settings
from journal.repositories.agents import Agents
from journal.repositories.scope import Scope
from journal.repositories.setting_rows import SettingRows

NO_ENVIRONMENT = 0


class PlanAgentCoordinator:
    """Whether the main agent of the current environment coordinates work through Plan agents."""

    def __init__(self, settings: SettingRows, catalogue: StatesCatalogue, agents: Agents, scope: Scope) -> None:
        self.settings, self.catalogue, self.agents, self.scope = settings, catalogue, agents, scope

    def is_coordinator(self) -> bool:
        settings = Settings.applied(self.settings, self.catalogue.floor_options())
        agent = self.agents.environment_main_agent(self.scope.id_default(NO_ENVIRONMENT))
        floor = (
            self.catalogue.selected_floor(settings)
            if agent is None
            else self.catalogue.floor(self.catalogue.stack(agent), settings, agent.role).bottom()
        )
        return self.catalogue.is_selected_floor(floor)
