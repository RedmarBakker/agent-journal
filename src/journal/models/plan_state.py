from enum import StrEnum


class PlanState(StrEnum):
    DRAFT = "draft"
    READY = "ready"
    REVIEWING = "reviewing"
    APPROVED = "approved"
    STARTED = "started"
    PAUSED = "paused"
    BLOCKED = "blocked"
    FINISHED = "done"
    CANCELLED = "cancelled"

    def is_closed(self) -> bool:
        return self in (PlanState.FINISHED, PlanState.CANCELLED)

    def is_unapproved(self) -> bool:
        return self in (PlanState.DRAFT, PlanState.READY, PlanState.REVIEWING)

    def is_startable(self) -> bool:
        return self in (PlanState.APPROVED, PlanState.PAUSED, PlanState.STARTED)

    def can_become(self, state: "PlanState") -> bool:
        return state == self or state in MOVES[self]


MOVES = {
    PlanState.DRAFT: {PlanState.READY, PlanState.REVIEWING, PlanState.APPROVED, PlanState.FINISHED, PlanState.CANCELLED},
    PlanState.READY: {PlanState.DRAFT, PlanState.REVIEWING, PlanState.APPROVED, PlanState.FINISHED, PlanState.CANCELLED},
    PlanState.REVIEWING: {PlanState.READY, PlanState.FINISHED, PlanState.CANCELLED},
    PlanState.APPROVED: {PlanState.STARTED, PlanState.PAUSED, PlanState.FINISHED, PlanState.CANCELLED},
    PlanState.STARTED: {PlanState.PAUSED, PlanState.BLOCKED, PlanState.FINISHED, PlanState.CANCELLED},
    PlanState.BLOCKED: {PlanState.STARTED, PlanState.PAUSED, PlanState.FINISHED, PlanState.CANCELLED},
    PlanState.PAUSED: {PlanState.READY, PlanState.APPROVED, PlanState.STARTED, PlanState.FINISHED, PlanState.CANCELLED},
    PlanState.FINISHED: {PlanState.STARTED},
    PlanState.CANCELLED: set(),
}
