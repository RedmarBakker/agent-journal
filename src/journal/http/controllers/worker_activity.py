from journal.http.support.request import Request
from journal.repositories.messages import Messages
from journal.support.card_kind import CardKind
from journal.support.response import Response

SHOWN = 30


class WorkerActivityController:
    """The workers' noteworthy moments, newest first, read from the marks already written for them in the chat: dispatches, ends, merges, test runs and steps."""

    def __init__(self, messages: Messages) -> None:
        self.messages = messages

    def recent(self, request: Request) -> Response:
        return Response.json({"rows": self.messages.newest_moments((CardKind.WORKERS, CardKind.WORKER_STEPS, CardKind.WORKER_TESTS), SHOWN)})
