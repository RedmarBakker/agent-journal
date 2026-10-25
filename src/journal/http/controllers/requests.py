from journal.features.tasks.support.hub_filing import REQUESTED_OF
from journal.http.support.model_fields import ModelFields
from journal.http.support.request import Request
from journal.models.user import User
from journal.repositories.links import Links
from journal.repositories.tasks import Tasks
from journal.support.response import Response


class RequestController:
    """The requests filed for the signed-in person, newest first, from every environment, the hub's among them."""

    def __init__(self, tasks: Tasks, links: Links) -> None:
        self.tasks, self.links = tasks, links

    def index(self, request: Request) -> Response:
        ids = [ref.id for ref in self.links.sources(User(id=int(request.actor.id)), REQUESTED_OF)]
        return Response.json({"rows": [ModelFields.build(task) for task in reversed(self.tasks.numbered_anywhere(ids))]})
