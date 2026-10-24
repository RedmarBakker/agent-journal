from typing import ClassVar

from journal.features.updates.support.release_notes import ReleaseNotes
from journal.events.data_source import DataSource


class UpdatesPart(DataSource[ReleaseNotes]):
    """The updates feature's part of the feature data."""

    name: ClassVar[str] = "updates"
