from journal.features.checks.support.check_runner import CheckRunner
from journal.db.query import Query
from journal.http.controllers.controller import Controller
from journal.http.support.request import Request
from journal.support.response import Response
from journal.models.check import Check
from journal.repositories.checks import Checks


class CheckController(Controller[Check]):
    """Checks the journal runs, with their last run, the project's own open and the ones a wait made for itself closed, under Waits; one is run now or force stopped from here, and its command and how often it runs are changed by an update."""

    def __init__(self, checks: Checks, runner: CheckRunner) -> None:
        self.repository, self.runner = checks, runner

    def list_query(self) -> Query:
        return self.repository.query().filter(is_retired=False)

    def open_rows(self, query: Query) -> Query:
        return query.filter(wait_target=False)

    def closed_rows(self, query: Query) -> Query:
        return query.filter(wait_target=True)

    def run(self, request: Request) -> Response:
        return Response.json(self.runner.start(self.repository.find(request.number("id")), request.actor))

    def stop(self, request: Request) -> Response:
        return Response.json(self.runner.stop(self.repository.find(request.number("id")), request.actor))
