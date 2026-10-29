from typing import ClassVar

from journal.events.data_source import DataSource
from journal.features.organization.support.organization_data import OrganizationData


class OrganizationPart(DataSource[OrganizationData]):
    """The organization feature's part of the feature data."""

    name: ClassVar[str] = "organization"
