from journal.http.support.request import Request
from journal.support.response import Response
from journal.supervisor_authority import SupervisorAuthority
from journal.supervisor_failure import SupervisorFailure
from journal.features.supervisor.support.supervisor_observations import SupervisorObservations


class SupervisorController:
    """Owner-authenticated management for the narrow v1 supervisor grant."""

    def __init__(self, authority: SupervisorAuthority, observations: SupervisorObservations) -> None:
        self.authority, self.observations = authority, observations

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
        if request.supervisor is None:
            return Response(403, {"error": "a supervisor service credential is required"})
        try:
            answer = self.observations.observe(request.supervisor, request.body)
        except SupervisorFailure as denied:
            return Response(denied.status, {"error": str(denied)})
        return Response(200, answer, {"Cache-Control": "no-store"})
