from journal.http.support.request import Request
from journal.services.service_hooks import ServiceHooks
from journal.services.service_registration import ServiceRegistration
from journal.support.response import Response
from journal.sync.sync_secret import SyncSecret


class ServiceController:
    """Where a service beside the journal registers its address and the events it wants posted, with the server's service secret, so no other local process and nothing from outside is posted the journal's events."""

    def __init__(self, hooks: ServiceHooks, secret: SyncSecret) -> None:
        self.hooks, self.secret = hooks, secret

    def register(self, request: Request) -> Response:
        if not self.secret.allows(request.headers):
            return Response.forbidden("a service registers with the server's service secret, straight, never through a proxy")
        self.hooks.register(ServiceRegistration(str(request.body["name"]), str(request.body["address"]), tuple(request.body.get("events", ()))))
        return Response.json({"registered": request.body["name"]})
