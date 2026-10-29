from typing import ClassVar

from journal.events.data_source import DataSource
from journal.features.workers.support.session_workers_data import SessionWorkersData


class SessionWorkersPart(DataSource[SessionWorkersData]):
    """The part of the feature data a worker's own session reads about the worker rows it runs as."""

    name: ClassVar[str] = "session_workers"

    @classmethod
    def missing(cls) -> SessionWorkersData:
        return SessionWorkersData()
