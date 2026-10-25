from datetime import datetime
from typing import TypeVar

from journal.db.connection import Connection
from journal.db.query import Query
from journal.events.bus import Bus
from journal.events.rows.row_event import RowEvent
from journal.support.actor import Actor
from journal.models.scoped import Scoped
from journal.models.support.ref import Ref
from journal.repositories.repository import Repository
from journal.repositories.scope import PROJECT, Scope

S = TypeVar("S", bound=Scoped)


class ScopedRepository(Repository[S]):
    """The same, within the scope's environment: every read sees only that environment's rows, so no read names it; a read across environments says so by its name; a new row that names none is placed in it; a row bound to it, or linked by one of member_links into a row bound to it, is read there and its events are heard there too."""

    member_links: tuple[str, ...] = ()

    def __init__(self, connection: Connection, bus: Bus, scope: Scope) -> None:
        super().__init__(connection, bus)
        self.scope = scope

    def with_project(self, query: Query) -> list[S]:
        return self._selected(query.filter_listed("environment_id", (self.scope.id, PROJECT)))

    def global_matching(self, **fields) -> list[S]:
        return self.selected_globally(self.query().filter(**fields).order("id"))

    def selected_globally(self, query: Query) -> list[S]:
        return self._selected(query)

    def maximum(self, query: Query, column: str, empty_value):
        return self.connection.result(*self._scoped(query).maximum(column, empty_value))["value"]

    def maximum_globally(self, query: Query, column: str, empty_value):
        return self.connection.result(*query.maximum(column, empty_value))["value"]

    def repeated(self, query: Query, column: str, minimum: int) -> list:
        return [row["value"] for row in self.connection.all(*self._scoped(query).repeated(column, minimum))]

    def scoped(self) -> list[S]:
        return self.all()

    def count(self) -> int:
        return self.counted(self.query())

    def scoped_rows(self) -> list[S]:
        return self.rows()

    def scoped_page(self, limit: int, previous: int | None = None) -> list[S]:
        return self.page(limit, previous)

    def _insert(self, row: S, actor: Actor, time: datetime) -> S:
        return super()._insert(self._placed(row), actor, time)

    def _scoped(self, query: Query) -> Query:
        bindings = self.scope.bound()
        return self._binding_scoped(query, bindings) if bindings else query.filter(environment_id=self.scope.id)

    def _binding_scoped(self, query: Query, bindings: tuple[Ref, ...]) -> Query:
        membership = self.link_query.filter_listed("kind", self.member_links).filter_listed("target", list(bindings)).filter_ref("source", self.query())
        environment_rows = self.query().filter(environment_id=self.scope.id)
        binding_rows = self.query().filter_listed("id", [ref.id for ref in bindings if ref.type == self.table])
        return query.filter_alternatives(environment_rows, binding_rows, self.query().filter_existing(membership))

    def _placed_event(self, event: RowEvent, row: S, actor: Actor) -> RowEvent:
        return super()._placed_event(event, row, actor).with_bound_environments(self.scope.binders(Ref.build(row), self.member_links))

    def _placed(self, row: S) -> S:
        return row if row.environment_id else row.with_(environment_id=self.scope.id)
