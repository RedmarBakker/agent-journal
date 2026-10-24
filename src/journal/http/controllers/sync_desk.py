from dataclasses import asdict

from journal.engine.lifecycle import Lifecycle
from journal.http.support.request import Request
from journal.support.response import Response
from journal.sync.server_doors import ServerDoors
from journal.sync.sync_secret import DESK_PROTOCOL, PROTOCOL_HEADER, SyncSecret
from journal.sync.sync_status import SyncStatus
from journal.sync.team_account import TeamAccount
from journal.sync.team_server_link import TeamServerLink
from sync_server.protocol import PROTOCOL, PROTOCOL_HEADER as TEAM_PROTOCOL_HEADER
from sync_server.full_copy import FullCopy
from sync_server.pull_answer import PullAnswer
from sync_server.sync_answer import SyncAnswer


class SyncDeskController:
    """The doors the sync service comes through to the server's SyncDesk: how to reach the team, the service's word on how it stands, the query a pull asks with, a pull answer handed in as the team server sent it, the queue's next batch taken out with the files waiting and the Team chat lease and row number blocks kept up, a push's result and the files sent handed back for the batch it names, the pull a push carried handed again after a full copy, the team's full copy laid in when it is past this journal's sequence, and an upgrade claimed and finished."""

    def __init__(self, doors: ServerDoors, secret: SyncSecret, lifecycle: Lifecycle, account: TeamAccount, link: TeamServerLink, status: SyncStatus) -> None:
        self.doors, self.secret, self.lifecycle = doors, secret, lifecycle
        self.account, self.link, self.status = account, link, status

    def guarded(self, door):
        return lambda request: self.answered(door, request)

    def answered(self, door, request: Request) -> Response:
        if not self.secret.allows(request):
            return Response.forbidden("the sync desk answers the sync service alone: a request carries the server's service secret and comes straight, never through a proxy")
        if request.headers.get(PROTOCOL_HEADER, "") != str(DESK_PROTOCOL):
            return Response(426, {"error": f"this journal server speaks version {DESK_PROTOCOL} of the sync desk's doors and its sync process version {request.headers.get(PROTOCOL_HEADER) or 'none'}: restart the journal so both run the same code"})
        if not self.lifecycle.is_booted():
            return Response.busy("the journal is starting: try again in a moment")
        return door(request)

    # whether this journal is in a team, and how the sync service reaches its server: the address, the headers each request carries, the certificate authority it trusts and the least protocol it takes an answer in
    def team(self, request: Request) -> Response:
        joined, root = self.account.is_joined(), self.account.root_path()
        return Response.json({"joined": joined, "address": self.account.address(), "headers": self.link.headers() if joined else {}, "authority": str(root) if root.is_file() else "", "protocol": {"header": TEAM_PROTOCOL_HEADER, "least": PROTOCOL}})

    def query(self, request: Request) -> Response:
        query = self.doors.query(request.queried("wait_seconds"))
        return Response.json({**asdict(query), "path": TeamServerLink.pull_path(query)})

    def state(self, request: Request) -> Response:
        self.status.reported(str(request.body.get("fault", "")), bool(request.body.get("reached", False)))
        return Response.json({})

    def batch(self, request: Request) -> Response:
        return Response.json(asdict(self.doors.batch()))

    def files_sent(self, request: Request) -> Response:
        self.doors.files_sent(tuple(request.body.get("ids", ())))
        return Response.json({})

    def pushed(self, request: Request) -> Response:
        ids = tuple(int(id) for id in str(request.query.get("ids", "")).split(",") if id)
        return Response.json(asdict(self.doors.batch_answered(ids, SyncAnswer.parsed(**request.body))))

    def delivery(self, request: Request) -> Response:
        return Response.json(asdict(self.doors.delivered(SyncAnswer.parsed(**request.body))))

    def answer(self, request: Request) -> Response:
        return Response.json(asdict(self.doors.answered(PullAnswer.parsed(**request.body))))

    def copy(self, request: Request) -> Response:
        return Response.json({"laid_in": self.doors.copied(FullCopy.parsed(**request.body))})

    def upgrade_claimed(self, request: Request) -> Response:
        self.doors.upgrade_claimed()
        return Response.json({})

    def upgrade_finished(self, request: Request) -> Response:
        self.doors.upgrade_finished()
        return Response.json({})
