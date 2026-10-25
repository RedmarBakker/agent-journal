from typing import ClassVar

from journal.db.migration import Migration

BEFORE = "written before the journal named reports and documents never acted on"


class SettledWrittenWork(Migration):
    """Every report and document written before the journal named those never acted on is signed off, so only work written from now on is followed up."""

    number: ClassVar[int] = 54
    statements: ClassVar[tuple[str, ...]] = (
        f"UPDATE reports SET settled_reason = '{BEFORE}' WHERE settled_reason IS NULL OR settled_reason = ''",
        f"UPDATE docs SET settled_reason = '{BEFORE}' WHERE settled_reason IS NULL OR settled_reason = ''",
    )
