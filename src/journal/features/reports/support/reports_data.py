from dataclasses import dataclass

from journal.features.reports.support.unacted_row import UnactedRow


@dataclass(frozen=True)
class ReportsData:
    """The reports feature's reading: whether an update the user has not read waits, when the agent was last offered to write one, and when the first commit after that offer or the last update was made, which starts the clock for the next offer; and the reports and documents never acted on."""

    unread_update: bool
    offered_at: float
    clock_start_at: float
    unacted: tuple[UnactedRow, ...] = ()
