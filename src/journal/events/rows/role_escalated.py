from dataclasses import dataclass

from journal.events.rows.row_event import RowEvent


@dataclass(frozen=True, kw_only=True)
class RoleEscalated(RowEvent):
    """A Role was stuck, refused or ended without clocking out, and its report went up the hub to the agent of the session named: its Domain agent, else the Plan agent."""

    feature_name = "organization"

    recipient: str
    report: str
