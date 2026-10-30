from typing import ClassVar

from journal.db.migration import Migration


class DuplicateSettingsDrop(Migration):
    """A setting stored twice in one environment, as the Developer features switch was when its old key was renamed onto a row already stored, keeps only its most recently changed row, so a change made since is the one read."""

    number: ClassVar[int] = 83
    statements: ClassVar[tuple[str, ...]] = (
        "DELETE FROM settings WHERE id IN (SELECT older.id FROM settings older JOIN settings newer ON newer.environment_id = older.environment_id AND newer.key = older.key AND newer.id != older.id"
        " WHERE newer.updated_at > older.updated_at OR (newer.updated_at = older.updated_at AND newer.id > older.id))",
    )
