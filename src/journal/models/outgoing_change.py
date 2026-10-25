from dataclasses import dataclass
from typing import ClassVar

from journal.models.model import Model

CREATED = "created"
UPDATED = "updated"
DELETED = "deleted"
WITHDRAWN = "withdrawn"
# a withdrawn row every journal keeps; any other keeper is the stamp of the one person whose journals keep it
KEPT_BY_ALL = "all"


@dataclass(frozen=True)
class OutgoingChange(Model):
    """One write of a shared row waiting to be sent to the team server: the row's table and number, whether it was created, updated, deleted or withdrawn from the team, the columns as stored with when each was changed, who wrote it, for a withdrawn row who keeps it, and the key of the team it goes to, none for the home team's. Stored on this machine."""

    shared: ClassVar[bool] = False
    timeline_visible: ClassVar[bool] = False

    row_table: str = ""
    row: int = 0
    action: str = ""
    fields: dict | None = None
    changed_at: dict | None = None
    writer: str = ""
    is_sending: bool = False
    kept_by: str = ""
    team_key: str = ""

    @classmethod
    def withdrawal(cls, row: Model, writer: str, kept_by: str) -> "OutgoingChange":
        return cls(row_table=row.table(), row=row.row_id, action=WITHDRAWN, fields={}, changed_at={}, writer=writer, kept_by=kept_by)

    def merged(self, later: "OutgoingChange") -> "OutgoingChange | None":
        if later.action in (DELETED, WITHDRAWN):
            return None if self.action == CREATED else self.with_(action=later.action, fields={}, changed_at={}, writer=later.writer, kept_by=later.kept_by)
        return self.with_(fields={**(self.fields or {}), **(later.fields or {})}, changed_at={**(self.changed_at or {}), **(later.changed_at or {})}, writer=later.writer)

    def payload(self) -> dict:
        return {"row_table": self.row_table, "row": self.row, "action": self.action, "actor": self.writer, "fields": self.fields or {}, "changed_at": self.changed_at or {}, "local_number": self.row_id, "kept_by": self.kept_by}
