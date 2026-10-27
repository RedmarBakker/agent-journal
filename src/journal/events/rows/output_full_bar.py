from dataclasses import dataclass

from journal.events.rows.row_event import RowEvent


@dataclass(frozen=True, kw_only=True)
class OutputFullBar(RowEvent):
    """A watched run's progress has stood at its whole bar while its command still runs: told once to the agent that ran it."""

    feature_name = "shell"

    run_session: str | None
    full_seconds: int
