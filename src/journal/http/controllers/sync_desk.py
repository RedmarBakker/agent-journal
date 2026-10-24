from dataclasses import asdict

from journal.engine.lifecycle import Lifecycle
from journal.http.support.request import Request
from journal.support.response import Response
from journal.sync.server_doors import ServerDoors
from journal.sync.sync_batch import SyncBatch
from journal.sync.sync_client import SyncClient
from journal.sync.sync_start import SyncStart
from journal.sync.sync_secret import SyncSecret
from sync_server.full_copy import FullCopy
from sync_server.pull_answer import PullAnswer
from sync_server.sync_answer import SyncAnswer


class SyncDeskController:
    """The local doors the sync's carrier comes through to the server's SyncDesk: the query a pull asks with, a pull answer handed in as the team server sent it, the queue's next batch taken out with the files waiting and the Team chat lease and row number blocks kept up, a push's result and the files sent handed back for the batch it names, the team's full copy laid in when it is past this journal's sequence, and, around an upgrade, the queue drained and the carrier paused, then resumed."""

    def __init__(self, doors: ServerDoors, client: SyncClient, sync: SyncStart, secret: SyncSecret, lifecycle: Lifecycle) -> None:
        self.doors, self.client, self.sync, self.secret, self.lifecycle = doors, client, sync, secret, lifecycle

    def guarded(self, door):
        return lambda request: self.answered(door, request)

    def answered(self, door, request: Request) -> Response:
        if not self.secret.allows(request):
            return Response.forbidden("the sync desk answers its carrier alone: a request carries the server's sync secret and comes straight, never through a proxy")
        if not self.lifecycle.is_booted():
            return Response.busy("the journal is starting: try again in a moment")
        return door(request)

    def query(self, request: Request) -> Response:
        return Response.json(asdict(self.doors.query(request.queried("wait_seconds"))))

    def batch(self, request: Request) -> Response:
        return Response.json(asdict(self.doors.batch(request.queried("wait_seconds"))))

    def files_sent(self, request: Request) -> Response:
        self.doors.files_sent(tuple(request.body.get("ids", ())))
        return Response.json({})

    def pushed(self, request: Request) -> Response:
        batch = SyncBatch(tuple(request.body.get("ids", ())), (), (), False)
        return Response.json(asdict(self.doors.pushed(batch, SyncAnswer.parsed(**request.body["answer"]))))

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

    def drain(self, request: Request) -> Response:
        self.sync.stopped()
        self.client.prepare_upgrade()
        return Response.json({"drained": self.doors.batch(0).is_empty(), "paused": True})

    def pause(self, request: Request) -> Response:
        self.sync.stopped()
        return Response.json({"paused": True})

    def resume(self, request: Request) -> Response:
        self.sync.run()
        return Response.json({"paused": False})
