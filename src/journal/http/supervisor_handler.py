from urllib.parse import urlsplit

from journal.http.handler import Handler
from journal.http.support.supervisor_authentication import SERVICE_PATHS
from journal.support.response import Response


class SupervisorHandler(Handler):
    """Serves only supervisor service routes, which the request funnel always checks for a service token."""

    def do_GET(self) -> None:
        self.close_connection = True
        self._answer(Response(403, {"error": "the Gateway listener serves token-checked supervisor routes only"}))

    def do_POST(self) -> None:
        if urlsplit(self.path).path not in SERVICE_PATHS:
            self.close_connection = True
            return self._answer(Response(403, {"error": "the Gateway listener serves token-checked supervisor routes only"}))
        super().do_POST()
