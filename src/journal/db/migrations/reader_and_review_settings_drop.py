from typing import ClassVar

from journal.db.connection import Connection
from journal.db.migration import Migration

# the options that are gone: the reader rules, now lines told once, and the limit on a reviewed plan, now the review sequence's steps
OPTION_KEYS = ("shell.reader_after", "shell.report_read_after", "shell.report_fix_after", "plans.review_ready_within", "sequences.stale_after")


class ReaderAndReviewSettingsDrop(Migration):
    """The settings rows of the reader rules' options, the reviewed plan's limit and the stale step's write count, all gone, are deleted, so the Settings page and the settings reader never meet a key no option names."""

    number: ClassVar[int] = 69

    def apply(self, connection: Connection) -> None:
        connection.execute(f"DELETE FROM settings WHERE key IN ({', '.join('?' for _ in OPTION_KEYS)})", OPTION_KEYS)
