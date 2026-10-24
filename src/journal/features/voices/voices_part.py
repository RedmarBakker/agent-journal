from typing import ClassVar

from journal.features.voices.support.voices_data import VoicesData
from journal.events.data_source import DataSource


class VoicesPart(DataSource[VoicesData]):
    """The voices feature's part of the feature data."""

    name: ClassVar[str] = "voices"
