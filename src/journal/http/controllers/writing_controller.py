from typing import TypeVar

from journal.http.controllers.controller import Controller
from journal.http.support.download_response import DownloadResponse
from journal.http.support.model_fields import ModelFields
from journal.http.listing import SHORT_PAGE_ROWS
from journal.http.support.request import Request
from journal.support.response import Response
from journal.models.doc import Doc
from journal.models.report import Report
from journal.repositories.messages import Messages
from journal.support.docx_export import DocxExport

W = TypeVar("W", Doc, Report)


class WritingController(Controller[W]):
    """What documents and reports share: a list reads each without its long fields, ten at a time, and the rows it links to and how many comments are under it are requested by id; a section is added at the end of the body."""

    page_rows = SHORT_PAGE_ROWS
    omitted_fields = ("body",)

    def shown_page(self, rows: list[W]) -> list[dict]:
        linked = self.repository.linked_rows(row.row_id for row in rows)
        comment_counts = self.repository.linking_counts(Messages.COMMENT_LINK, [row.row_id for row in rows])
        return [{**ModelFields.build(row), "links": self.links(row, linked), "comment_count": comment_counts.get(row.id, 0)} for row in rows]

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
