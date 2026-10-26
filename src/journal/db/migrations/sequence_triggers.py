import json
from typing import ClassVar

from journal.db.connection import Connection
from journal.db.migration import Migration

# the trigger action that started a sequence by the user's words, frozen here as it was before a sequence held its own triggers
SEQUENCE_ACTION = "sequence"


class SequenceTriggers(Migration):
    """A sequence holds its triggers as records: its trigger event becomes a row trigger, and every trigger row that started a sequence by the user's words becomes a phrase trigger on the sequence it names and is deleted; the trigger event column is dropped."""

    number: ClassVar[int] = 70

    def apply(self, connection: Connection) -> None:
        columns = {row["name"] for row in connection.all("PRAGMA table_info(sequences)")}
        if "trigger_event" not in columns:
            return
        if "triggers" not in columns:
            connection.execute("ALTER TABLE sequences ADD COLUMN triggers TEXT DEFAULT '[]'")
        phrases = self.sequence_phrases(connection)
        for row in connection.all("SELECT id, title, trigger_event FROM sequences"):
            records = [{"kind": "row", "moment": row["trigger_event"]}] if row["trigger_event"] else []
            records += [{"kind": "phrase", "text": phrase} for phrase in phrases.get(row["title"], [])]
            connection.execute("UPDATE sequences SET triggers = ? WHERE id = ?", (json.dumps(records), row["id"]))
        if self.has_table(connection, "triggers"):
            connection.execute("DELETE FROM triggers WHERE action = ?", (SEQUENCE_ACTION,))
        connection.execute("ALTER TABLE sequences DROP COLUMN trigger_event")

    def sequence_phrases(self, connection: Connection) -> dict[str, list[str]]:
        phrases: dict[str, list[str]] = {}
        if not self.has_table(connection, "triggers"):
            return phrases
        for row in connection.all("SELECT text, phrases FROM triggers WHERE action = ?", (SEQUENCE_ACTION,)):
            phrases.setdefault(row["text"], []).extend(json.loads(row["phrases"] or "[]"))
        return phrases
