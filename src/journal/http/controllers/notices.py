from datetime import datetime, timezone

from journal.db.query import Query
from journal.http.controllers.controller import Controller
from journal.http.listing import SHORT_PAGE_ROWS
from journal.http.counts import Counts
from journal.http.support.request import Request
from journal.support.response import Response
from journal.models.notice import Notice
from journal.repositories.notices import Notices


class NoticeController(Controller[Notice]):
    """Notices pinned for the user, open until closed, listed twenty at a time."""

    repository: Notices
    page_rows = SHORT_PAGE_ROWS

    def __init__(self, notices: Notices) -> None:
        self.repository = notices

    def open_rows(self, query: Query) -> Query:
        return query.filter_null("closed_at")

    def closed_rows(self, query: Query) -> Query:
        return query.filter_present("closed_at")

    def counts(self, query: Query) -> Counts:
        return Counts(all=self.repository.count(), open=self.repository.open_count(), unread=self.repository.unviewed())

    def close(self, request: Request) -> Response:
        notice = self.repository.find(request.number("id"))
        return Response.json(self.repository.save(notice.closed(datetime.now(timezone.utc)), request.actor))
