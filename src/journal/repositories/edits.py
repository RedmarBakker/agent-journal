from journal.support.code_files import CodeFiles
from journal.db.connection import Connection
from journal.events.bus import Bus
from journal.support.actor import Actor
from journal.models.edit import Edit
from journal.repositories.scope import Scope
from journal.repositories.scoped_repository import ScopedRepository

EDIT_ROWS = 500


class Edits(ScopedRepository[Edit]):
    model = Edit

    def __init__(self, connection: Connection, bus: Bus, scope: Scope) -> None:
        super().__init__(connection, bus, scope)

    def record(self, edit: Edit, actor: Actor) -> Edit:
        stored = self.save(edit, actor)
        for old in self.selected(self.query().with_columns("session").order_descending("id").offset(EDIT_ROWS)):
            self.delete(old, actor)
        return stored

    def tool_use_edits(self, session: str, tool_use: int) -> list[Edit]:
        return self.selected(self.query().filter(session=session, tool_use=tool_use).without("old_text", "new_text").order("id"))

    def agent_edits(self, session: str, start: float, last: int, ceiling_id: int = 0) -> list[Edit]:
        query = self.query().filter(session=session).filter_greater("time", start)
        return list(reversed(self.selected((query.filter_less("id", ceiling_id) if ceiling_id else query).order_descending("id").limit(last))))

    def has_older(self, session: str, first: int) -> bool:
        return bool(self.selected(self.query().filter(session=session).filter_less("id", first).limit(1)))

    def code_line_count(self, session: str, start_at: float) -> int:
        lines = self.grouped_sums(self.query().filter(session=session).filter_greater("time", start_at), "path", "added", "removed")
        return sum(count for path, count in lines.items() if CodeFiles.has_code((path,)))
