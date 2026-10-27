from journal.http.support.request import Request
from journal.repositories.environments import Environments
from journal.support.response import Response
from journal.supervisor_link import SupervisorLink


class SupervisedProcessController:
    """Every process the supervisors of this journal's environments run, read from each supervisor that answers: the agent's terminal, the server, the engines, each plugin's services, the share tunnel and the workers' sessions, each with its environment, its state, when it last started and its process id."""

    def __init__(self, link: SupervisorLink, environments: Environments) -> None:
        self.link, self.environments = link, environments

    def index(self, request: Request) -> Response:
        rows = [{"environment": environment.name, **vars(process)} for environment in self.link.running(self.environments.all()) for process in self.link.processes(environment.row_id)]
        return Response.json({"processes": rows})
