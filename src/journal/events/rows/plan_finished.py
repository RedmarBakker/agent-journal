from dataclasses import dataclass

from journal.events.rows.plan_closed import PlanClosed
from journal.models.plan_mode import PlanMode


@dataclass(frozen=True, kw_only=True)
class PlanFinished(PlanClosed):
    """A plan finished, with its plan mode."""

    mode: PlanMode
