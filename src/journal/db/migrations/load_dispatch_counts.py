import json
from typing import ClassVar

from journal.db.connection import Connection
from journal.db.migration import Migration

# the keys of a stored load's dispatch counts and its busy and low stretches, as they were and as they are named now
KEY_NAMES = {"dispatches_for": "calm_dispatches", "dispatches_against": "busy_dispatches", "over_minutes": "busy_minutes", "under_minutes": "low_minutes"}
QUEUE_COLUMNS = ("work_queue", "message_queue")


class LoadDispatchCounts(Migration):
    """The dispatch counts and the stretches of every load kept on an agent's row, its work and message queues and the load of each work mode, take their plain names: the dispatches made while the load was low and those made while it grew, and the minutes it has stayed busy and low."""

    number: ClassVar[int] = 71

    def apply(self, connection: Connection) -> None:
        columns = {row["name"] for row in connection.all("PRAGMA table_info(agents)")}
        if "mode_loads" not in columns:
            return
        for row in connection.all("SELECT id, work_queue, message_queue, mode_loads FROM agents"):
            queues = {column: with_key_names(json.loads(row[column] or "{}")) for column in QUEUE_COLUMNS}
            modes = {mode: with_key_names(queue) for mode, queue in json.loads(row["mode_loads"] or "{}").items()}
            connection.execute("UPDATE agents SET work_queue = ?, message_queue = ?, mode_loads = ? WHERE id = ?", (json.dumps(queues["work_queue"]), json.dumps(queues["message_queue"]), json.dumps(modes), row["id"]))


def with_key_names(queue: dict) -> dict:
    return {KEY_NAMES.get(key, key): value for key, value in queue.items()}
