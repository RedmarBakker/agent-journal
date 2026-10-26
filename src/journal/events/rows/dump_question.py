from dataclasses import dataclass

from journal.events.rows.row_event import RowEvent


@dataclass(frozen=True, kw_only=True)
class DumpQuestion(RowEvent):
    """The agent asked the user a question on a dump, in the dump's window."""

    feature_name = "dumps"

    dump_id: int
