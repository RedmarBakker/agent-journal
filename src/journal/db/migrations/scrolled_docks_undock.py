from typing import ClassVar

from journal.db.migration import Migration

# the newest messages of a chat the viewer shows on its first page; a resting docked card older than these was out of sight before 4.69.8
SHOWN_MESSAGE_COUNT = 50


class ScrolledDocksUndock(Migration):
    """A row's card left docked but out of sight, older than its chat's first page and neither running nor leaving, is taken down, so the docked list that now holds every docked card shows what was shown before."""

    number: ClassVar[int] = 84
    statements: ClassVar[tuple[str, ...]] = (
        "UPDATE messages SET data = json_set(data, '$.docked', json('false')) WHERE json_extract(data, '$.docked') = 1"
        " AND coalesce(json_extract(data, '$.active'), 0) = 0 AND json_extract(data, '$.undock_at') IS NULL"
        f" AND id < coalesce((SELECT shown.id FROM messages shown WHERE shown.environment_id IS messages.environment_id ORDER BY shown.id DESC LIMIT 1 OFFSET {SHOWN_MESSAGE_COUNT - 1}), 0)",
    )
