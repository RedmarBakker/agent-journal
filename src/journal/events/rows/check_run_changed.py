from dataclasses import dataclass

from journal.events.rows.row_event import RowEvent


@dataclass(frozen=True, kw_only=True)
class CheckRunChanged(RowEvent):
    """A check's run started, ended or was stopped: the check, when its run started, which names the run, and whether a task waits on the check rather than the agent."""

    feature_name = "checks"

    check_id: int
    run_start: float
    wait_target: bool
