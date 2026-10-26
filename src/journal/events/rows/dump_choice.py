from dataclasses import dataclass

from journal.events.rows.row_event import RowEvent


@dataclass(frozen=True, kw_only=True)
class DumpChoice(RowEvent):
    """The user chose a next step on a dump, left it to the agent (pick -1) or described what to do in their own words (pick -2)."""

    feature_name = "dumps"

    dump_id: int
    choice: int
    label: str
