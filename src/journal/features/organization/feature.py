from journal.features.feature import Feature
from journal.features.organization.commands.organization_command import OrganizationCommand
from journal.features.organization.organization_nudges import OrganizationNudges
from journal.features.organization.organization_part import OrganizationPart
from journal.features.organization.role_conduct import RoleConduct
from journal.features.organization.support.organization_data import OrganizationData
from journal.features.organization.support.organization_data_reader import OrganizationDataReader
from journal.support.agent_role import AgentRole


class OrganizationFeature(Feature[OrganizationData]):
    name = OrganizationPart.name
    title = "Agentic organization"
    help = "The domains and Roles of an agentic organization are read from the folder the Settings page names; journal holds no list of them. Each Role is one value that solo and seats both use, and a worker dispatched to a Role works inside its tools and approvals."
    commands = (OrganizationCommand,)
    data = (OrganizationDataReader,)
    helper_conduct = {AgentRole.WORKER: (RoleConduct,)}
    nudges = (OrganizationNudges.ROLE_WRITES_NOTHING, OrganizationNudges.ACTION_WAITS_FOR_USER)
