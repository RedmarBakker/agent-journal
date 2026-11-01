from typing import ClassVar

from journal.db.connection import Connection
from journal.db.migration import Migration


class AgentModesAndProfiles(Migration):
    """Agents from the removed modes become main agents, mode data is dropped, and old worker profile names take the shipped names."""

    number: ClassVar[int] = 89

    def apply(self, connection: Connection) -> None:
        columns = self.column_names(connection, "agents")
        if "mode" in columns:
            connection.execute("UPDATE agents SET role = 'main' WHERE mode IN ('builder', 'orchestrator', 'solo')")
            connection.execute("ALTER TABLE agents DROP COLUMN mode")
        if "mode_loads" in columns:
            connection.execute("ALTER TABLE agents DROP COLUMN mode_loads")
        connection.execute("UPDATE sent_agents SET profile = 'journal-medior' WHERE profile = 'medior'")
        connection.execute("UPDATE sent_agents SET profile = 'journal-senior' WHERE profile = 'senior'")
