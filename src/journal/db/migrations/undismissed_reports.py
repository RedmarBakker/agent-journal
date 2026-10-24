from typing import ClassVar

from journal.db.migration import Migration


class UndismissedReports(Migration):
    """A reader report never dismissed, which stored its dismissal as an empty text, stores none, as a report's absent dismissal is now kept."""

    number: ClassVar[int] = 47
    statements: ClassVar[tuple[str, ...]] = ("UPDATE reader_reports SET dismissal = NULL WHERE dismissal = ''",)
