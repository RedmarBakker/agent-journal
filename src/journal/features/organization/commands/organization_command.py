from argparse import Namespace

from journal.console.command import Command
from journal.features.organization.support.organization import Organization
from journal.features.organization.support.contracts import Contracts
from journal.support.caller import Caller


class OrganizationCommand(Command):
    """journal organization: the domains the organization folder holds with their Roles, each Role's cardinality, whether it writes and its models, then the files that broke the schema and the version read; reload reads the folder again."""

    noun = "organization"
    default_verb = "list"

    def __init__(self, organization: Organization) -> None:
        self.organization = organization

    def arguments(self, verbs) -> None:
        self.verb(verbs, "list", "list the domains with their Roles, the problems found in the files and the version read")
        self.verb(verbs, "reload", "read the organization folder again, then list it")

    def list(self, args: Namespace, caller: Caller) -> int:
        self.print_contracts(self.organization.contracts())
        return 0

    def reload(self, args: Namespace, caller: Caller) -> int:
        self.print_contracts(self.organization.reload())
        return 0

    @staticmethod
    def print_contracts(contracts: Contracts) -> None:
        if contracts.is_empty() and not contracts.problems:
            print("no organization: set the agentic organization folder on the Settings page")
        for domain in contracts.domains:
            print(f"domain {domain.id}: {domain.title}")
            for role in contracts.roles_of(domain.id):
                print(f"  role {role.id}: {role.cardinality}, {'writes' if role.writes else 'does not write'}, claude {role.models.claude}, codex {role.models.codex} on {role.models.effort}")
        for problem in contracts.problems:
            print(f"{problem.severity} {problem.path}: {problem.message}")
        if contracts.version:
            print(f"version {contracts.version}")
