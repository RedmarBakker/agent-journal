from journal.features.organization.support.organization import Organization
from journal.features.organization.support.organization_data import OrganizationData
from journal.features.organization.support.role_approvals import RoleApprovals
from journal.models.agent import Agent


class OrganizationDataReader:
    """Reads the organization feature's part of the feature data for an agent."""

    def __init__(self, organization: Organization, approvals: RoleApprovals) -> None:
        self.organization, self.approvals = organization, approvals

    def read(self, agent: Agent) -> OrganizationData:
        return OrganizationData(self.organization.contracts(), dict(self.organization.history), self.approvals)
