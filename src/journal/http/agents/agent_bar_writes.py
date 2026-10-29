from journal.models.agent import Agent
from journal.providers.providers import Providers
from journal.supervisor_link import SupervisorLink
from journal.support.rejection import Rejection


class AgentBarWrites:
    """What the agent bar changes on a live agent: its model or effort, and a line typed into its terminal."""

    def __init__(self, providers: Providers, supervisor: SupervisorLink) -> None:
        self.providers, self.supervisor = providers, supervisor

    def control(self, agent: Agent, action: str, value: str) -> None:
        provider = self.providers.lookup(agent.provider)
        choice = next((c for g in provider.controls["groups"] if g["key"] == action for c in g["choices"] if c["value"] == value), None)
        if choice is None:
            raise Rejection(f"{action} {value} is not a choice the agent bar offers")
        self.supervisor.choose(agent.environment_id, choice["command"])

    def shell(self, agent: Agent, command: str) -> None:
        self.supervisor.type_raw(agent.environment_id, command)
