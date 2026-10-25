from dataclasses import fields
from typing import Generic, TypeVar

from journal.http.counts import Counts
from journal.http.row_list import RowList
from journal.db.query import Query
from journal.http.listing import LISTING_ROW_LIMIT, Listing
from journal.http.row_list_page import RowListPage
from journal.http.support.request import Request
from journal.support.response import Response
from journal.models.model import Model
from journal.repositories.repository import Repository

S = TypeVar("S", bound=Model)


class Controller(Generic[S]):
    """One per model: its list, one row, a new one and a change, over its repository as the request's environment sees it. Its list is a query its repository pages, filters and counts in SQL: its own rows alone unless list_query says which, with what index_page adds of each row's own, and reads no relationship of them; a resource whose rows close names its open and its closed rows as filters of that query; one that shows more than its fields says what in shown_page; one whose rows are wide pages fewer of them at a time."""

    repository: Repository[S]
    page_rows: int = LISTING_ROW_LIMIT

    def index(self, request: Request) -> Response:
        return Response.json(self.listed(Listing.query_listing(request.query)))

    def listed(self, listing: Listing) -> RowList:
        listing, query = listing.capped(self.page_rows), self.list_query()
        if listing.ids:
            rows = self.id_rows(listing.ids)
            return RowList(rows=self.shown_page(rows), is_last_page=True, counts=self.counts(query))
        with self.repository.listing():
            page = self.list_page(listing, query)
            return RowList(rows=self.index_page(page["rows"]), is_last_page=page["is_last_page"], counts=self.counts(query))

    def list_page(self, listing: Listing, query: Query) -> RowListPage:
        return listing.listed(self.repository, query, self.open_rows(query), self.closed_rows(query))

    def index_page(self, rows: list[S]) -> list:
        return list(rows)

    def list_query(self) -> Query:
        return self.repository.query()

    def open_rows(self, query: Query) -> Query:
        return query

    def closed_rows(self, query: Query) -> Query:
        return query.filter_listed("id", ())

    def id_rows(self, ids: tuple[int, ...]) -> list[S]:
        return self.repository.selected(self.list_query().filter_listed("id", sorted(ids)).order("id"))

    def counts(self, query: Query) -> Counts:
        return Counts(all=self.repository.counted(query), open=self.repository.counted(self.open_rows(query)), unread=0)

    def shown(self, row: S) -> object:
        return self.shown_page([row])[0]

    def shown_page(self, rows: list[S]) -> list:
        return list(rows)

    def show(self, request: Request) -> Response:
        return Response.json(self.shown(self.repository.find(request.number("id"))))

    def store(self, request: Request) -> Response:
        row = self.repository.model(**self.fields(request.body))
        return Response.json(self.shown(self.repository.save(row, request.actor)), 201)

    def update(self, request: Request) -> Response:
        row = self.repository.find(request.number("id"))
        return Response.json(self.shown(self.repository.save(row.with_(**self.fields(request.body)), request.actor)))

    def delete(self, request: Request) -> Response:
        self.repository.delete(self.repository.find(request.number("id")), request.actor)
        return Response.json({})

    def fields(self, body: dict) -> dict:
        owned = {f.name for f in fields(self.repository.model)} - {"id", "environment_id", "created_at", "creator", "updated_at", "updater", "state"}
        return {name: value for name, value in body.items() if name in owned}
