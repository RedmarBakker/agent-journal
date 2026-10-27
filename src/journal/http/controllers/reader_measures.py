from dataclasses import asdict

from journal.features.shell.support.reader_measures import ReaderMeasures
from journal.http.support.request import Request
from journal.support.response import Response


class ReaderMeasureController:
    """How well the environment's readers read its runs, for the Developer tab."""

    def __init__(self, measures: ReaderMeasures) -> None:
        self.measures = measures

    def index(self, request: Request) -> Response:
        return Response.json(asdict(self.measures.measurement()))
