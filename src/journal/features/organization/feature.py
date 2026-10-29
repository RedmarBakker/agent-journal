from journal.features.feature import Feature
from journal.features.organization.commands.organization_command import OrganizationCommand


class OrganizationFeature(Feature):
    name = "organization"
    title = "Agentic organization"
    help = "The domains and Roles of an agentic organization are read from the folder the Settings page names; journal holds no list of them. Each Role is one value that solo and seats both use."
    commands = (OrganizationCommand,)
