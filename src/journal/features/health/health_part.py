from typing import ClassVar

from journal.events.data_source import DataSource
from journal.features.health.support.unchecked_work import UncheckedWork


class HealthPart(DataSource[UncheckedWork]):
    """The health feature's part of the feature data."""

    name: ClassVar[str] = "health"
