from typing import ClassVar

from journal.features.dumps.support.dumps_data import DumpsData
from journal.events.data_source import DataSource


class DumpsPart(DataSource[DumpsData]):
    """The dumps feature's part of the feature data."""

    name: ClassVar[str] = "dumps"
