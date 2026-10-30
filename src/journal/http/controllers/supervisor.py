from typing import Any, Callable

from journal.features.supervisor.support.supervisor_maintenance import SupervisorMaintenance
from journal.features.supervisor.support.supervisor_observations import SupervisorObservations
from journal.http.support.request import Request
from journal.repositories.scope import Scope
from journal.support.response import Response
from journal.supervisor_authority import SupervisorAuthority
from journal.supervisor_failure import SupervisorFailure
from journal.supervisor_principal import SupervisorPrincipal


class SupervisorController:
    """Owner grant management and private supervisor bridge endpoints."""

    def __init__(self, authority: SupervisorAuthority, observations: SupervisorObservations,
                 maintenance: SupervisorMaintenance, scope: Scope) -> None:
        self.authority, self.observations, self.maintenance = authority, observations, maintenance
        self.scope = scope

    def enroll(self, request: Request) -> Response:
        try:
            grant, token = self.authority.enroll(request.actor, request.body)
        except SupervisorFailure as denied:
            return Response(denied.status, {"error": str(denied)})
        return Response(201, grant, {"X-Journal-Supervisor-Token": token, "Cache-Control": "no-store"})

    def change(self, request: Request) -> Response:
        try:
            grant, token = self.authority.change(request.actor, request.body)
        except SupervisorFailure as denied:
            return Response(denied.status, {"error": str(denied)})
        headers = {"Cache-Control": "no-store"}
        if token:
            headers["X-Journal-Supervisor-Token"] = token
        return Response(200, grant, headers)

    def observe(self, request: Request) -> Response:
        return self._service(request, self.observations.observe)

    def admit(self, request: Request) -> Response:
        return self._service(request, self.observations.admit)

    def apply(self, request: Request) -> Response:
        return self._service(request, self.maintenance.apply_maintenance)

    def receipt(self, request: Request) -> Response:
        return self._service(request, self._receipt)

    def _service(self, request: Request, operation: Callable[[SupervisorPrincipal, object], dict[str, Any]]) -> Response:
        principal = request.supervisor
        if principal is None:
            return Response(403, {"error": "a supervisor service credential is required"})
        try:
            with self.scope.environment(principal.scope["environment_id"]):
                answer = operation(principal, request.body)
        except SupervisorFailure as denied:
            return Response(denied.status, {"error": str(denied)})
        return Response(200, answer, {"Cache-Control": "no-store"})

    def _receipt(self, principal: SupervisorPrincipal, body: object) -> dict[str, Any]:
        action_id = self._receipt_action_id(body)
        return self.maintenance.receipt(principal, action_id)

    @staticmethod
    def _receipt_action_id(body: object) -> str:
        if (not isinstance(body, dict) or set(body) != {"protocol_version", "action_id"}
                or type(body["protocol_version"]) is not int or body["protocol_version"] != 1
                or not isinstance(body["action_id"], str) or not 1 <= len(body["action_id"]) <= 256):
            raise SupervisorFailure(400, "the supervisor receipt request is invalid")
        return body["action_id"]
