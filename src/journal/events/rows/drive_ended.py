from dataclasses import dataclass

from journal.events.rows.row_event import RowEvent


@dataclass(frozen=True, kw_only=True)
class DriveEnded(RowEvent):
    """A hub plan or task this environment drove is driven from it no longer, since it was deleted or closed on another journal or its lease was taken over: name says which row as a line names it, noun what it is, and reason what happened."""

    feature_name = "plans"

    name: str
    noun: str
    reason: str
