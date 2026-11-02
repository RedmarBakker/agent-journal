from typing import ClassVar

from journal.db.connection import Connection
from journal.db.migration import Migration


class SupervisorGrantPause(Migration):
    """Existing version two supervisor grants remain on when the pause control is added."""

    number: ClassVar[int] = 92

    def apply(self, connection: Connection) -> None:
        connection.execute(
            "UPDATE entries SET data = json_set(data, '$.grant_v2.paused', json('false')) "
            "WHERE entry_type = 'SupervisorGrant' AND json_type(data, '$.grant_v2') = 'object' "
            "AND json_type(data, '$.grant_v2.paused') IS NULL"
        )
