from typing import ClassVar

from journal.features.sequences.support.sequences_data import SequencesData
from journal.events.data_source import DataSource


class SequencesPart(DataSource[SequencesData]):
    """The sequences feature's part of the feature data."""

    name: ClassVar[str] = "sequences"
