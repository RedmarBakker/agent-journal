from journal.engine.base_state import BaseState
from journal.engine.states_catalogue import StatesCatalogue
from journal.engine.support.settings import Settings
from journal.support.agent_role import AgentRole
from journal.repositories.agents import Agents
from journal.repositories.scope import Scope
from journal.repositories.setting_rows import SettingRows

# read outside any environment, as a measure on the worker thread is, the work mode's own floor answers
NO_ENVIRONMENT = 0


class WorkMode:
    """The floor of the scope environment's main agent as the settings place it, or the floor the settings pick while the environment has no main agent, asked what it does, for code that runs outside the stack: a command, a listener, a measure."""

    def __init__(self, settings: SettingRows, catalogue: StatesCatalogue, agents: Agents, scope: Scope) -> None:
        self.settings, self.catalogue, self.agents, self.scope = settings, catalogue, agents, scope

    def state(self) -> type[BaseState]:
        settings = Settings.applied(self.settings, self.catalogue.mode_options())
        agent = self.agents.environment_main_agent(self.scope.id_default(NO_ENVIRONMENT))
        if agent is None:
            return self.catalogue.mode_state(settings)
        return type(self.catalogue.floor(self.catalogue.stack(agent), settings, AgentRole.MAIN).states[0])

    def delegates_work(self) -> bool:
        return self.state().delegates_work()
