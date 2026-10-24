from journal.features.client_errors.support.client_error_intake import ClientErrorIntake
from journal.http.support.request import Request
from journal.support.response import Response


class ClientErrorController:
    """The console errors the viewer posts."""

    def __init__(self, intake: ClientErrorIntake) -> None:
        self.intake = intake

    def store(self, request: Request) -> Response:
        self.intake.record(str(request.body.get("message", "")), str(request.body.get("stack", "")))
        return Response.json({"recorded": True})
