from typing import ClassVar

from journal.features.plans.support.plans_data import PlansData
from journal.events.data_source import DataSource


class PlansPart(DataSource[PlansData]):
    """The plans feature's part of the feature data."""

    name: ClassVar[str] = "plans"
