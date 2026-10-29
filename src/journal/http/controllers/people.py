from journal.http.support.request import Request
from journal.repositories.users import Users
from journal.support.response import Response
from journal.sync.hosting import Hosting
from journal.sync.team_account import TeamAccount


class PeopleController:
    """Who the viewer is: the viewer's own user number, whoever signed in on a hosted journal, and this machine's device, every person by number and name, so the viewer says you only for its own person, and whether this journal is hosted for the team's browsers, where the viewer offers to sign out."""

    def __init__(self, account: TeamAccount, users: Users, hosting: Hosting) -> None:
        self.account, self.users, self.hosting = account, users, hosting

    def show(self, request: Request) -> Response:
        people = [{"id": user.row_id, "name": user.name} for user in self.users.rows()]
        return Response.json({"me": request.actor.number(), "device": self.account.device(), "people": people, "hosted": self.hosting.is_hosted()})
