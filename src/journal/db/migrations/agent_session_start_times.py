from typing import ClassVar

from journal.db.connection import Connection
from journal.db.migration import Migration


class AgentSessionStartTimes(Migration):
    """A live main agent row keeps its latest session start even when the record is trimmed."""

    number: ClassVar[int] = 90

    def apply(self, connection: Connection) -> None:
        connection.execute(
            "UPDATE agents SET session_started_at = ("
            "SELECT entries.created_at FROM entries "
            "WHERE entries.entry_type = 'SessionStarted' "
            "AND entries.actor = 'agent:' || agents.session "
            "ORDER BY entries.created_at DESC, entries.id DESC LIMIT 1) "
            "WHERE agents.role = 'main' AND agents.state != 'ended' "
            "AND agents.session != '' AND agents.session_started_at IS NULL "
            "AND EXISTS (SELECT 1 FROM entries WHERE entries.entry_type = 'SessionStarted' "
            "AND entries.actor = 'agent:' || agents.session)"
        )
