from dataclasses import dataclass

from journal.events.rows.task_assignment_opportunity import TaskAssignmentOpportunity


@dataclass(frozen=True, kw_only=True)
class TaskReopened(TaskAssignmentOpportunity):
    """A task became open again after a wait ended or its plan restarted."""

    feature_name = "tasks"

    task_id: int
    reason: str
