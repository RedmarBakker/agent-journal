from datetime import datetime, timezone

from journal.http.controllers.writing_controller import WritingController
from journal.http.support.request import Request
from journal.support.response import Response
from journal.models.report import Report
from journal.repositories.reports import Reports
from journal.support.time_source import TimeSource


class ReportController(WritingController[Report]):
    """What was checked or researched, written up here, and the updates the user reads, whose items a list leaves out with the body, each marked read when the user first opens it."""

    repository: Reports
    omitted_fields = ("body", "items")

    def __init__(self, reports: Reports, time_source: TimeSource) -> None:
        self.time_source = time_source
        self.repository = reports

    def read(self, request: Request) -> Response:
        report = self.repository.find(request.number("id"))
        return Response.json(self.shown(self.repository.save(report.read(self.time_source.moment()), request.actor)))
