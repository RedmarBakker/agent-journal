from typing import ClassVar

from journal.features.triggers.support.triggers_data import TriggersData
from journal.events.data_source import DataSource


class TriggersPart(DataSource[TriggersData]):
    """The triggers feature's part of the feature data."""

    name: ClassVar[str] = "triggers"
