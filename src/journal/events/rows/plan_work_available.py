from dataclasses import dataclass

from journal.events.rows.task_assignment_opportunity import TaskAssignmentOpportunity


@dataclass(frozen=True, kw_only=True)
class PlanWorkAvailable(TaskAssignmentOpportunity):
    """Eligible plan work became available to its bound Plan agent."""

    feature_name = "plans"

    plan_id: int = 0
    phase_id: int = 0
    task_id: int = 0
    receipt_id: int = 0
