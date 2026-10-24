from typing import TypeVar

from journal.http.controllers.controller import Controller
from journal.http.support.download_response import DownloadResponse
from journal.http.support.model_fields import ModelFields
from journal.http.support.request import Request
from journal.support.response import Response
from journal.models.doc import Doc
from journal.models.report import Report
from journal.support.docx_export import DocxExport

W = TypeVar("W", Doc, Report)


class WritingController(Controller[W]):
    """What documents and reports share: a list includes each without its body and the rows it links to, which are requested by id; a section is added at the end of the body."""

    def index_page(self, rows: list[W]) -> list[dict]:
        return [{name: value for name, value in ModelFields.build(row).items() if name != "body"} for row in rows]

    def shown_page(self, rows: list[W]) -> list[dict]:
        linked = self.repository.linked_rows(row.row_id for row in rows)
        return [{**ModelFields.build(row), "links": self.links(row, linked)} for row in rows]

    @staticmethod
    def links(row: W, linked: dict) -> list[str]:
        return [str(ref) for ref in linked.get(row.id, [])]

    def export(self, request: Request) -> DownloadResponse:
        row = self.repository.find(request.number("id"))
        exported = DocxExport.build(row.title, row.abstract, row.body, f"{row.noun()} {row.id}")
        return DownloadResponse(exported.kind, exported.body, name=exported.name)

    def section(self, request: Request) -> Response:
        row = self.repository.find(request.number("id"))
        body = f"{row.body.rstrip()}\n\n## {request.body.get('title', '')}\n\n{request.body.get('body', '')}\n"
        return Response.json(self.shown(self.repository.save(row.with_(body=body), request.actor)))
