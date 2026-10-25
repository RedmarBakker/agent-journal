from journal.features.tasks.support.hub_filer import REQUESTER_LINK, TEAM_REQUEST
from journal.features.tasks.support.task_holders import TaskHolders
from journal.models.support.ref import Ref
from journal.models.task import DECLINED, Task
from journal.repositories.environments import Environments
from journal.http.support.model_fields import ModelFields
from journal.http.support.request import Request
from journal.models.user import User
from journal.repositories.links import Links
from journal.repositories.tasks import Tasks
from journal.repositories.users import Users
from journal.support.response import Response


class RequestController:
    """The requests filed for the signed-in person or for the whole team, an issue never among them, and those the signed-in person filed with the state each has reached, newest first, from every environment, the hub's among them."""

    def __init__(self, tasks: Tasks, links: Links, users: Users, environments: Environments, holders: TaskHolders) -> None:
        self.tasks, self.links, self.users, self.environments, self.holders = tasks, links, users, environments, holders

    def index(self, request: Request) -> Response:
        ids = sorted({*(ref.id for ref in self.links.sources(User(id=int(request.actor.id)), REQUESTER_LINK)), *(link.source.id for link in self.links.of_kind(TEAM_REQUEST))})
        return Response.json({"rows": [ModelFields.build(task) for task in reversed(self.tasks.tasks_numbered(ids))]})

    def filed(self, request: Request) -> Response:
        ids = sorted({link.source.id for kind in (REQUESTER_LINK, TEAM_REQUEST) for link in self.links.of_kind(kind)})
        mine = self.tasks.creator_tasks(ids, request.actor)
        drivers = self.tasks.row_holders(mine)
        return Response.json({"rows": [self.standing(task, drivers) for task in reversed(mine)]})

    def standing(self, task: Task, drivers: dict[int, Ref]) -> dict:
        state = "declined" if task.is_declined() else task.state
        return {**ModelFields.build(task), "standing": state, "reason": task.outcome.removeprefix(DECLINED) if task.is_declined() else "", "for_whom": self.recipient(task),
                "driver": self.holders.name(drivers[task.row_id]) if task.row_id in drivers else "", "done_at": task.completed_at.isoformat() if task.completed_at else ""}

    def recipient(self, task: Task) -> str:
        people = [self.users.find(ref.id).name for ref in self.links.targets(task, REQUESTER_LINK)]
        hubs = [self.environments.find(ref.id).team_name for ref in self.links.targets(task, TEAM_REQUEST)]
        return ", ".join([*people, *(f"the {name} team" for name in hubs)])
