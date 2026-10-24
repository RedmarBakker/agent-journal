from typing import ClassVar

from journal.features.pins.support.pins_data import PinsData
from journal.events.data_source import DataSource


class PinsPart(DataSource[PinsData]):
    """The pins feature's part of the feature data."""

    name: ClassVar[str] = "pins"
