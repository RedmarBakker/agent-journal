from typing import Callable

from journal.features.pausing.agent_pause import AgentPause
from journal.features.schedules.job_stop import JobStop
from journal.models.agent import Agent
from journal.providers.providers import Providers
from journal.repositories.agents import Agents
from journal.repositories.environment_owners import EnvironmentOwners
from journal.repositories.environments import Environments
from journal.repositories.scope import Scope
from journal.supervisor_link import SupervisorLink
from journal.support.actor import Actor
from journal.support.host_writer import HostWriter
from journal.support.rejection import Rejection
from sync_server.host_request import HostRequest

AGENT_CONTROL = "agent_control"
AGENT_PAUSE = "agent_pause"
AGENT_RESUME = "agent_resume"
AGENT_SHELL = "agent_shell"
AGENT_JOB_STOP = "agent_job_stop"


class AgentBarWrites(HostWriter):
    """What the agent bar changes on a live agent, its model or effort, its pause and its resume, a line typed into its terminal, made here for this journal's own agent and, asked by the environment's owner from another journal of the team, made here as the host; a request from anyone but the owner is refused here, where the agent runs."""

    def __init__(self, agents: Agents, providers: Providers, supervisor: SupervisorLink, pausing: AgentPause, job_stop: JobStop, environments: Environments, owners: EnvironmentOwners, scope: Scope) -> None:
        self.agents, self.providers, self.supervisor, self.pausing, self.job_stop = agents, providers, supervisor, pausing, job_stop
        self.environments, self.owners, self.scope = environments, owners, scope

    def makers(self) -> dict[str, Callable[[HostRequest], None]]:
        return {AGENT_CONTROL: self.remote_control, AGENT_PAUSE: self.remote_pause, AGENT_RESUME: self.remote_resume, AGENT_SHELL: self.remote_shell, AGENT_JOB_STOP: self.remote_job_stop}

    def control(self, agent: Agent, action: str, value: str) -> None:
        provider = self.providers.lookup(agent.provider)
        choice = next((c for g in provider.controls["groups"] if g["key"] == action for c in g["choices"] if c["value"] == value), None)
        if choice is None:
            raise Rejection(f"{action} {value} is not a choice the agent bar offers")
        self.supervisor.choose(agent.environment_id, choice["command"])

    def shell(self, agent: Agent, command: str) -> None:
        self.supervisor.type_raw(agent.environment_id, command)

    def remote_shell(self, request: HostRequest) -> None:
        self.owner_changes(request, lambda agent: self.shell(agent, request.body["command"]))

    def remote_control(self, request: HostRequest) -> None:
        self.owner_changes(request, lambda agent: self.control(agent, request.body["action"], request.body["value"]))

    def remote_pause(self, request: HostRequest) -> None:
        self.owner_changes(request, lambda agent: self.pausing.pause(agent, Actor.user(request.account_id)))

    def remote_resume(self, request: HostRequest) -> None:
        self.owner_changes(request, lambda agent: self.pausing.resume(agent, Actor.user(request.account_id)))

    def remote_job_stop(self, request: HostRequest) -> None:
        self.owner_changes(request, lambda agent: self.job_stop.stop(agent, request.body["job_id"], Actor.user(request.account_id)))

    def owner_changes(self, request: HostRequest, change: Callable[[Agent], object]) -> None:
        for agent in self.owner_agents(request):
            try:
                change(agent)
            except Rejection as refused:
                print(f"host request {request.id} on agent {agent.id} was refused: {refused}", flush=True)

    def owner_agents(self, request: HostRequest) -> list[Agent]:
        agents = []
        for environment in self.environments.keyed(request.environment_key):
            if self.owners.owner_number(environment.row_id) != request.account_id:
                print(f"host request {request.id} asks to change the agent in {environment.name}, which is not user {request.account_id}'s: refused", flush=True)
                continue
            with self.scope.environment(environment.row_id):
                agents.append(self.agents.find(request.body["agent_id"]))
        return agents
