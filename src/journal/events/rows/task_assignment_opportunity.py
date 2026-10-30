from journal.events.rows.row_event import RowEvent


class TaskAssignmentOpportunity(RowEvent):
    """A row event after which the current task assigner may take work at a safe moment."""
