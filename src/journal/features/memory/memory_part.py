from typing import ClassVar

from journal.features.memory.support.memory_data import MemoryData
from journal.events.data_source import DataSource


class MemoryPart(DataSource[MemoryData]):
    """The memory feature's part of the feature data."""

    name: ClassVar[str] = "memory"
