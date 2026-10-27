from dataclasses import dataclass

from journal.events.rows.row_event import RowEvent


@dataclass(frozen=True, kw_only=True)
class OutputWithoutTotal(RowEvent):
    """A watched test run or build prints as it goes but shows no count of a total, so its card has no bar: told once to the agent that runs it."""

    feature_name = "shell"

    run_session: str | None
