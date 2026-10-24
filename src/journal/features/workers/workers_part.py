from typing import ClassVar

from journal.features.workers.support.workers_data import WorkersData
from journal.events.data_source import DataSource


class WorkersPart(DataSource[WorkersData]):
    """The workers feature's part of the feature data."""

    name: ClassVar[str] = "workers"
