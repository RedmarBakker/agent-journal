from typing import ClassVar

from journal.features.tasks.support.tasks_data import TasksData
from journal.events.data_source import DataSource


class TasksPart(DataSource[TasksData]):
    """The tasks feature's part of the feature data."""

    name: ClassVar[str] = "tasks"
