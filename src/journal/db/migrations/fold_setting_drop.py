from typing import ClassVar

from journal.db.migration import Migration


class FoldSettingDrop(Migration):
    """Chat marks no longer fold into the one before them, since the team's conflict marks were the only kind that did, so the setting of the fold window is deleted."""

    number: ClassVar[int] = 80
    statements: ClassVar[tuple[str, ...]] = ("DELETE FROM settings WHERE key = 'messages.fold_marks_seconds'",)
