from dataclasses import asdict

from journal.engine.agent_launcher import AgentLauncher
from journal.features.hydration.support.session_hydration import SessionHydration
from journal.providers.providers import Providers
from journal.repositories.agents import Agents
from journal.http.controllers.controller import Controller
from journal.http.support.request import Request
from journal.support.response import Response
from journal.models.environment import Environment
from journal.repositories.environments import Environments
from journal.supervisor_link import SupervisorLink
from journal.config import Config
from journal.http.support.model_fields import ModelFields
from journal.support.worktree import Worktree
from journal.repositories.environment_owners import EnvironmentOwners
from journal.support.rejection import Rejection
from journal.features.team.support.start_rule import StartRule


class EnvironmentController(Controller[Environment]):
    """The project's environments; one is made here, its chat filled from a conversation an agent program kept for the project when one is named, an agent is started in one from here, stopped, or the environment removed with everything in it; the project's kept conversations are listed for the form."""

    repository: Environments

    def __init__(self, environments: Environments, launcher: AgentLauncher, supervisor: SupervisorLink, config: Config, owners: EnvironmentOwners, starts: StartRule,
                 hydration: SessionHydration, providers: Providers, agents: Agents) -> None:
        self.repository, self.launcher, self.supervisor, self.config = environments, launcher, supervisor, config
        self.owners, self.starts, self.hydration, self.providers, self.agents = owners, starts, hydration, providers, agents

    def rows(self) -> list[Environment]:
        return self.repository.all()

    def shown_page(self, rows: list[Environment]) -> list[dict]:
        return [{**ModelFields.build(row), "worktree": next(iter(Worktree(self.config.root, row.name).badges()), "")} for row in rows]

    def store(self, request: Request) -> Response:
        name, session = request.body.get("name", "").strip(), request.body.get("session", "")
        if not name:
            raise Rejection("an environment needs a name")
        if session and self.repository.matching(name=name):
            raise Rejection(f"environment {name} exists already: a session fills only a new environment's chat")
        environment = self.repository.lookup(name)
        if session:
            self.hydration.hydrate(environment, request.body.get("provider", "claude"), session, request.actor)
        return Response.json(environment, 201)

    def sessions(self, request: Request) -> Response:
        names = {environment.row_id: environment.name for environment in self.repository.all()}
        session_environments = {agent.session: names.get(agent.environment_id, "") for agent in self.agents.all_agents()}
        rows = [{**asdict(conversation), "title": provider.title, "environment": session_environments.get(conversation.session, "")} for provider in self.providers.all() for conversation in provider.past_sessions(self.config.root)]
        return Response.json(sorted(rows, key=lambda row: row["updated_at"], reverse=True))

    def launch(self, request: Request) -> Response:
        environment = self.repository.find(request.number("id"))
        refusal = self.starts.refusal(environment, request.actor.number())
        if refusal:
            raise Rejection(refusal)
        self.launcher.start(environment.name, request.body.get("agent", "claude"))
        return Response.json(environment)

    def stop(self, request: Request) -> Response:
        environment = self.repository.find(request.number("id"))
        refusal = self.owners.write_refusal(request.actor, environment)
        if refusal:
            raise Rejection(refusal)
        self.supervisor.stop(environment.row_id)
        return Response.json(environment)

    def remove(self, request: Request) -> Response:
        environment = self.repository.find(request.number("id"))
        self.repository.wipe(environment, request.actor)
        return Response.json({"worktree": Worktree(self.config.root, environment.name).dropped()})
