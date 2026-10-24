from typing import ClassVar

from journal.features.hydration.support.hydration_data import HydrationData
from journal.events.data_source import DataSource


class HydrationPart(DataSource[HydrationData]):
    """The hydration feature's part of the feature data."""

    name: ClassVar[str] = "hydration"
