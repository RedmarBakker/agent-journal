from journal.features.tasks.support.hub_filing import REQUESTED_OF, TEAM_REQUEST
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
    """The requests filed for the signed-in person, and those the signed-in person filed with the state each has reached, newest first, from every environment, the hub's among them."""

    def __init__(self, tasks: Tasks, links: Links, users: Users, environments: Environments, holders: TaskHolders) -> None:
        self.tasks, self.links, self.users, self.environments, self.holders = tasks, links, users, environments, holders

    def index(self, request: Request) -> Response:
        ids = [ref.id for ref in self.links.sources(User(id=int(request.actor.id)), REQUESTED_OF)]
        return Response.json({"rows": [ModelFields.build(task) for task in reversed(self.tasks.numbered_anywhere(ids))]})

    def filed(self, request: Request) -> Response:
        ids = sorted({link.source.id for kind in (REQUESTED_OF, TEAM_REQUEST) for link in self.links.of_kind(kind)})
        mine = [task for task in self.tasks.numbered_anywhere(ids) if task.creator == request.actor]
        drivers = self.tasks.row_holders(mine)
        return Response.json({"rows": [self.standing(task, drivers) for task in reversed(mine)]})

    def standing(self, task: Task, drivers: dict[int, Ref]) -> dict:
        state = "declined" if task.is_declined() else task.state
        return {**ModelFields.build(task), "standing": state, "reason": task.outcome.removeprefix(DECLINED) if task.is_declined() else "", "for_whom": self.recipient(task),
                "driver": self.holders.name(drivers[task.row_id]) if task.row_id in drivers else "", "done_at": task.finished_at.isoformat() if task.finished_at else ""}

    def recipient(self, task: Task) -> str:
        links = [link for link in self.links.link_rows(task) if link.source == Ref.build(task) and link.kind in (REQUESTED_OF, TEAM_REQUEST)]
        people = [self.users.find(link.target.id).name for link in links if link.kind == REQUESTED_OF]
        hubs = [self.environments.find(link.target.id).team_name for link in links if link.kind == TEAM_REQUEST]
        return ", ".join([*people, *(f"the {name} team" for name in hubs)])
