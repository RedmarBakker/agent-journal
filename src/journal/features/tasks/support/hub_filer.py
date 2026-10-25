from argparse import Namespace

from journal.console.support.hub_choice import HubChoice
from journal.models.link import Link
from journal.models.support.ref import Ref
from journal.models.task import Task
from journal.repositories.links import Links
from journal.repositories.users import Users
from journal.support.actor import Actor
from journal.support.rejection import Rejection

REQUESTER_LINK = "requested_of"
TEAM_REQUEST = "requested_of_team"
ISSUE = "issue"


class HubFiler:
    """A request or an issue is a task filed in the hub: --to files a request for one person, linked requested_of to them, --to-team a request for the whole team, linked to the hub, and --issue an issue on the board, linked to the hub as an issue."""

    def __init__(self, choice: HubChoice, users: Users, links: Links) -> None:
        self.choice, self.users, self.links = choice, users, links

    @staticmethod
    def is_filing(args: Namespace) -> bool:
        return bool(args.to or args.to_team or args.issue)

    def is_addressed(self, task: Task, person: int) -> bool:
        return bool(self.links.targets(task, TEAM_REQUEST)) or Ref("users", person) in self.links.targets(task, REQUESTER_LINK)

    def team(self, args: Namespace) -> str:
        return self.choice.hub(args.team).team_name if self.is_filing(args) else args.team

    def person(self, args: Namespace) -> int:
        people = self.users.with_name(args.to) if args.to else []
        if args.to and not people:
            raise Rejection(f"no person on the team is named {args.to}")
        return people[0].row_id if people else 0

    def link(self, task: Task, args: Namespace, person: int, team: str, actor: Actor) -> None:
        if not self.is_filing(args):
            return
        hub = Ref("environments", self.choice.hub(team).row_id)
        links = [(Ref("users", person), REQUESTER_LINK)] if person else []
        links += [(hub, TEAM_REQUEST)] if args.to_team else []
        links += [(hub, ISSUE)] if args.issue else []
        for target, kind in links:
            self.links.save(Link(source=Ref.build(task), target=target, kind=kind), actor)
