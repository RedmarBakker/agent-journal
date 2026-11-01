from contextlib import nullcontext
from urllib.parse import unquote

from journal.features.faults.support.request_time_recorder import RequestTimeRecorder

from journal.support.rejection import Rejection
from journal.support.missing_row import MissingRow
from journal.http.support.file_response import FileResponse
from journal.http.support.request import Request
from journal.features.faults.support.stall_watch import StallWatch
from journal.http.support.stream_response import StreamResponse
from journal.support.response import Response
from journal.http.support.route import Answer, Handler, Route
from journal.http.support.viewer_presence import ViewerPresence
from journal.http.support.project_check import ProjectCheck
from journal.repositories.scope import Scope


class Router:
    """Finds the route a request takes and answers it inside the environment the request names, or in none for an unscoped route."""

    def __init__(self, scope: Scope, presence: ViewerPresence, recorder: RequestTimeRecorder, stalls: StallWatch, projects: ProjectCheck) -> None:
        self.projects = projects
        self.scope, self.presence, self.recorder, self.stalls = scope, presence, recorder, stalls
        self.routes: list[Route] = []

    def get(self, path: str, handler: Handler) -> None:
        self.routes.append(Route("GET", path, handler))

    def post(self, path: str, handler: Handler) -> None:
        self.routes.append(Route("POST", path, handler))

    def get_unscoped(self, path: str, handler: Handler) -> None:
        self.routes.append(Route("GET", path, handler, scoped=False))

    def post_unscoped(self, path: str, handler: Handler) -> None:
        self.routes.append(Route("POST", path, handler, scoped=False))

    def get_outward(self, path: str, handler: Handler) -> None:
        self.routes.append(Route("GET", path, handler, outward=True))

    def matched(self, request: Request) -> Route | None:
        matching = self.match(request)
        return None if matching is None else matching[0]

    def match(self, request: Request) -> tuple[Route, dict[str, str]] | None:
        return next(((route, params) for route in self.routes if (params := route.params(request.method, request.path)) is not None), None)

    def page(self, request: Request) -> Response | FileResponse:
        answer = self.route(request)
        return Response.refused(f"{request.method} {request.path} streams, so it is no page") if isinstance(answer, StreamResponse) else answer

    def route(self, request: Request) -> Answer:
        if self.projects.is_other(request.headers):
            return self.projects.refusal(request.headers)
        self.presence.record(request.headers)
        matching = self.match(request)
        if matching is None:
            return Response.absent(f"{request.method} {request.path}")
        route, params = matching
        try:
            with self.scope.requested(lambda: request.environment, request.actor) if route.scoped else nullcontext():
                if route.outward:
                    return route.handler(request.with_params({name: unquote(value) for name, value in params.items()}))
                timer = self.recorder.begin(request.request_at)
                try:
                    self.stalls.begin(f"{request.method} {request.measured_path()}")
                    try:
                        answer = route.handler(request.with_params({name: unquote(value) for name, value in params.items()}))
                    finally:
                        self.stalls.end()
                except BaseException:
                    self.recorder.discarded(timer)
                    raise
                self.recorder.measured(timer, request.method, request.measured_path(), timer.wall_ms())
                return answer
        except Rejection as refused:
            return Response.refused(str(refused))
        except MissingRow as missing:
            return Response.missing(missing)
