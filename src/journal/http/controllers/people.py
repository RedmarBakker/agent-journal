from journal.http.support.request import Request
from journal.repositories.users import Users
from journal.support.response import Response


class PeopleController:
    """Who the viewer is: the viewer's own user number and every person by number and name, so the viewer says you only for its own person."""

    def __init__(self, users: Users) -> None:
        self.users = users

    def show(self, request: Request) -> Response:
        people = [{"id": user.row_id, "name": user.name} for user in self.users.rows()]
        return Response.json({"me": request.actor.number(), "people": people})
