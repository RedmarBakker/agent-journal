from journal.db.connection import Connection
from journal.events.bus import Bus
from journal.models.doc import Doc
from journal.models.doc_revision import DocRevision
from journal.repositories.linked_rows import LinkedRows
from journal.repositories.links import Links
from journal.db.query import Query
from journal.repositories.doc_scope import DocScope
from journal.repositories.scope import Scope
from journal.repositories.scoped_repository import ScopedRepository
from journal.support.actor import Actor
from journal.support.rejection import Rejection

REVISION_LINK = "revision_of"


class DocRevisions(ScopedRepository[DocRevision], LinkedRows):
    """A document's revisions, each linked to it, read in their order."""

    link_kind = REVISION_LINK
    model = DocRevision

    def __init__(self, connection: Connection, bus: Bus, scope: Scope, links: Links, visible: DocScope) -> None:
        super().__init__(connection, bus, scope)
        self.links, self.visible = links, visible

    def _scoped(self, query: Query) -> Query:
        return query.filter_listed("environment_id", self.visible.visible())

    def _placed(self, row: DocRevision) -> DocRevision:
        return row if row.environment_id else row.with_(environment_id=self.visible.own())

    def document_revisions(self, doc: Doc) -> list[DocRevision]:
        return sorted(self.children(doc), key=lambda revision: revision.number)

    def moved(self, doc: Doc, environment_id: int, actor: Actor) -> None:
        for revision in self.document_revisions(doc):
            self.save(revision.with_(environment_id=environment_id), actor)

    def latest(self, doc: Doc) -> DocRevision | None:
        revisions = self.document_revisions(doc)
        return revisions[-1] if revisions else None

    def close(self, doc: Doc, time: float, actor: Actor) -> DocRevision:
        latest = self.latest(doc)
        if latest is None:
            raise Rejection(f"doc {doc.id} has no revision to keep yet: its first edit opens one")
        if not latest.is_open(time):
            raise Rejection(f"revision {latest.number} of doc {doc.id} is already kept")
        return self.save(latest.closed(), actor)
