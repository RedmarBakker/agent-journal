from dataclasses import asdict

from journal.http.support.request import Request
from journal.support.response import Response
from journal.sync.sync_client import BATCH_ROWS, SyncClient
from journal.sync.sync_desk import SyncDesk
from sync_server.pull_answer import PullAnswer
from sync_server.sync_answer import SyncAnswer


class SyncDeskController:
    """The local doors the sync's carrier comes through to the server's SyncDesk: a pull answer handed in as the team server sent it, the queue's next batch taken out with the files waiting, a push's result handed back for the batch it names, and the carrier paused and resumed around an upgrade."""

    def __init__(self, desk: SyncDesk, client: SyncClient) -> None:
        self.desk, self.client = desk, client

    def answer(self, request: Request) -> Response:
        return Response.json({"applied": self.desk.answered(PullAnswer.parsed(**request.body))})

    def batch(self, request: Request) -> Response:
        with self.desk.held(self.desk.sending, "take a batch"):
            changes = self.desk.batch(BATCH_ROWS)
        return Response.json({"ids": [change.id for change in changes], "changes": [change.payload() for change in changes], "query": asdict(self.desk.query(0))})

    def pushed(self, request: Request) -> Response:
        return Response.json({"applied": self.desk.pushed_rows(list(request.body.get("ids", ())), SyncAnswer.parsed(**request.body["answer"]))})

    def pause(self, request: Request) -> Response:
        self.client.stop()
        return Response.json({"paused": True})

    def resume(self, request: Request) -> Response:
        self.client.start()
        return Response.json({"paused": False})
