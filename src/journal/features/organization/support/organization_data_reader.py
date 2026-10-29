from journal.features.organization.support.organization import Organization
from journal.features.organization.support.organization_data import OrganizationData
from journal.models.agent import Agent


class OrganizationDataReader:
    """Reads the organization feature's part of the feature data for an agent."""

    def __init__(self, organization: Organization) -> None:
        self.organization = organization

    def read(self, agent: Agent) -> OrganizationData:
        return OrganizationData(self.organization.contracts())
