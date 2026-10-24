from typing import ClassVar

from journal.features.briefing.support.briefing_data import BriefingData
from journal.events.data_source import DataSource


class BriefingPart(DataSource[BriefingData]):
    """The briefing feature's part of the feature data."""

    name: ClassVar[str] = "briefing"
