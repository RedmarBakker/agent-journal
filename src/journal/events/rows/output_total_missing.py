from dataclasses import dataclass

from journal.events.rows.row_event import RowEvent


@dataclass(frozen=True, kw_only=True)
class OutputTotalMissing(RowEvent):
    """A test run or build prints as it goes but its reader shows no count of a total, so its card has no bar: told once per version of the reader to the agent that runs it, with the pattern that reads its count when it prints one."""

    feature_name = "shell"

    run_session: str | None
    count_pattern: str = ""
