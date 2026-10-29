from dataclasses import dataclass

from journal.events.rows.row_event import RowEvent
from journal.models.board_phase import BoardPhase


@dataclass(frozen=True, kw_only=True)
class PlanEnteredBoardPhase(RowEvent):
    """A plan entered a phase on a domain's board, since that domain's tasks in it reached it."""

    feature_name = "organization"

    plan_id: int
    domain: str
    phase: BoardPhase
