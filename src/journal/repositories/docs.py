from datetime import datetime

from journal.models.doc import Doc
from journal.support.actor import Actor
from journal.db.connection import Connection
from journal.db.query import Query
from journal.events.bus import Bus
from journal.repositories.doc_scope import DocScope
from journal.repositories.scope import PROJECT, Scope
from journal.repositories.scoped_repository import ScopedRepository


class Docs(ScopedRepository[Doc]):
    model = Doc

    def unsettled(self) -> list[Doc]:
        return self.selected(self.query().filter(settled_reason="").order("id"))

    def __init__(self, connection: Connection, bus: Bus, scope: Scope, visible: DocScope) -> None:
        super().__init__(connection, bus, scope)
        self.visible = visible

    def of_project(self, doc: Doc, actor: Actor) -> Doc:
        with self.scope.environment(PROJECT):
            return self.save(doc, actor)

    def imported_for_project(self, doc: Doc, time: datetime, actor: Actor) -> Doc:
        with self.scope.environment(PROJECT):
            return self.imported(doc, time, actor)

    def _scoped(self, query: Query) -> Query:
        return query.filter_listed("environment_id", self.visible.visible())

    def _placed(self, row: Doc) -> Doc:
        return row if row.environment_id else row.with_(environment_id=self.visible.own())

    def recent_docs(self, start: datetime, end: datetime) -> list[Doc]:
        return self.selected(self.query().filter_greater_equal("created_at", start).filter_less("created_at", end).order("id"))

    def titled(self, title: str) -> bool:
        return bool(self.matching(title=title))
