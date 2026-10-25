from typing import ClassVar

from journal.config import Config
from journal.db.connection import Connection
from journal.db.migration import Migration
from journal.sync.team_account import TeamAccount


class EnvironmentTeams(Migration):
    """The Team chat becomes a session and every shared environment carries the team's key, unknown until the team server names it to a journal that has not learnt it, the flags they were marked by dropped; and every document and revision from before documents had an environment is the project's, in environment 0."""

    number: ClassVar[int] = 52

    def apply(self, connection: Connection) -> None:
        columns = {row["name"] for row in connection.all("PRAGMA table_info(environments)")}
        team_key = TeamAccount(Config(connection.path.parent.parent)).team_key()
        if "is_team_chat" in columns:
            connection.execute("UPDATE environments SET kind = 'session', team_key = ? WHERE is_team_chat = 1", (team_key,))
            connection.execute("ALTER TABLE environments DROP COLUMN is_team_chat")
        if "is_shared_with_team" in columns:
            connection.execute("UPDATE environments SET team_key = ? WHERE is_shared_with_team = 1 AND kind = 'local'", (team_key,))
            connection.execute("ALTER TABLE environments DROP COLUMN is_shared_with_team")
        for table in ("docs", "doc_revisions"):
            connection.execute(f"UPDATE {table} SET environment_id = 0 WHERE environment_id IS NULL")
