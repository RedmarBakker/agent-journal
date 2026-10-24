from typing import ClassVar

from journal.engine.demand_progress import DemandProgress
from journal.events.data_source import DataSource


class DemandsPart(DataSource[tuple[DemandProgress, ...]]):
    """The engine's part of the feature data: the agent's progress on every declared demand."""

    name: ClassVar[str] = "demands"

    @classmethod
    def missing(cls) -> tuple[DemandProgress, ...]:
        return ()
