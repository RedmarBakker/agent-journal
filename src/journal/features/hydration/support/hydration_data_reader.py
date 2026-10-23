from journal.features.hydration.support.hydration_data import HydrationData
from journal.models.agent import Agent
from journal.repositories.messages import Messages
from journal.repositories.scope import Scope


class HydrationDataReader:
    """Reads the hydration feature's part of the feature data for an agent: the session its environment's chat was filled from, while no agent has been asked to read it."""

    def __init__(self, messages: Messages, scope: Scope) -> None:
        self.messages, self.scope = messages, scope

    def read(self, agent: Agent) -> HydrationData:
        with self.scope.environment(agent.environment_id):
            hydrations = self.messages.new_hydrations()
        return HydrationData(hydrations[0].data["provider"], hydrations[0].data["session"]) if hydrations else HydrationData()
