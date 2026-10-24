from typing import ClassVar

from journal.events.data_source import DataSource
from journal.features.client_errors.support.client_errors_data import ClientErrorsData


class ClientErrorsPart(DataSource[ClientErrorsData]):
    """The client errors feature's part of the feature data."""

    name: ClassVar[str] = "client_errors"
