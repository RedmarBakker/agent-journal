from dataclasses import dataclass

from journal.events.rows.row_event import RowEvent


@dataclass(frozen=True, kw_only=True)
class OutputQuiet(RowEvent):
    """A background test run or build has printed nothing since it began, long enough to show it holds its output back: told once to the agent that ran it."""

    feature_name = "shell"

    run_session: str | None
    quiet_seconds: int
