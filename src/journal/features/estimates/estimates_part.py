from typing import ClassVar

from journal.engine.support.lazy_facts import LazyFacts
from journal.events.data_source import DataSource


class EstimatesPart(DataSource[LazyFacts]):
    """The estimates feature's forecast and risk facts."""

    name: ClassVar[str] = "estimates"
