from typing import ClassVar

from journal.features.reports.support.reports_data import ReportsData
from journal.events.data_source import DataSource


class ReportsPart(DataSource[ReportsData]):
    """The reports feature's part of the feature data."""

    name: ClassVar[str] = "reports"
