from dataclasses import dataclass

from journal.events.rows.task_assignment_opportunity import TaskAssignmentOpportunity


@dataclass(frozen=True, kw_only=True)
class TaskReopened(TaskAssignmentOpportunity):
    """A blocked task was opened again, with the reason it opened as a clause: question 12 was answered or closed."""

    feature_name = "tasks"

    task_id: int
    reason: str
