from journal.events.announcer import Announcer
from journal.events.moments.edit_dropped import EditDropped
from journal.events.moments.edit_kept import EditKept
from journal.models.model import Model
from journal.models.support.ref import Ref
from journal.repositories.links import Links
from journal.repositories.outgoing_changes import OutgoingChanges
from journal.repositories.scope import PROJECT
from journal.repositories.shared_tables import SharedTables
from journal.support.actor import Actor
from sync_server.rejected_field import RejectedField


class RejectedEdits:
    """The edits the team server rejected, put right on this machine: a field takes the value that stands, unless this machine has edited it again since, and a row deleted in the meantime is deleted here too; a card in the chat of the row's environment says whose edit was stored."""

    def __init__(self, tables: SharedTables, outgoing: OutgoingChanges, links: Links, announcer: Announcer) -> None:
        self.tables, self.outgoing, self.links, self.announcer = tables, outgoing, links, announcer

    def apply(self, rejections: tuple[RejectedField, ...]) -> None:
        for rejection in rejections:
            if self.tables.has(rejection.row_table):
                self.applied(rejection)

    def applied(self, rejection: RejectedField) -> None:
        if rejection.is_deleted_row():
            self.deleted(rejection)
        elif rejection.field not in self.outgoing.queued_fields(rejection.row_table, rejection.row):
            for row in self.tables.rows(rejection.row_table).pulled_update(rejection.row, {rejection.field: rejection.value}, Actor.system()):
                self.announcer.announce(EditKept(environment_id=self.environment(row), writer=rejection.writer, noun=row.noun(), row_id=row.row_id, field=rejection.field, kept=str(rejection.value), ref=Ref.build(row)))

    def deleted(self, rejection: RejectedField) -> None:
        self.outgoing.dropped(rejection.row_table, rejection.row, Actor.system())
        for row in self.tables.rows(rejection.row_table).pulled_deletion(rejection.row, Actor.system()):
            self.links.remove_links(row, Actor.system())
            self.announcer.announce(EditDropped(environment_id=self.environment(row), noun=row.noun(), row_id=row.row_id))

    @staticmethod
    def environment(row: Model) -> int:
        return getattr(row, "environment_id", PROJECT)
