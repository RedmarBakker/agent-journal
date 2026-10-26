from dataclasses import dataclass

from journal.events.rows.row_event import RowEvent


@dataclass(frozen=True, kw_only=True)
class ClockOutTestRunChanged(RowEvent):
    """The test run the journal makes of a worker's named tests at its clock-out started or ended."""

    feature_name = "workers"

    turn: int
