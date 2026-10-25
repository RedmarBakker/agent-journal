from typing import ClassVar

from journal.events.data_source import DataSource
from journal.features.reviewing.support.reviewing_data import ReviewingData


class ReviewingPart(DataSource[ReviewingData]):
    """The reviewing feature's part of the feature data."""

    name: ClassVar[str] = "reviewing"
