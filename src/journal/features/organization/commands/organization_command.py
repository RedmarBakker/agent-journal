from argparse import Namespace

from journal.console.command import Command
from journal.features.organization.support.board_phases import BoardPhases
from journal.features.organization.support.domain_plan import DomainPlan
from journal.features.organization.support.domain_plans import DomainPlans
from journal.features.organization.support.organization import Organization
from journal.features.organization.support.contracts import Contracts
from journal.support.caller import Caller

NO_ORGANIZATION = "no organization: set the agentic organization folder on the Settings page"


class OrganizationCommand(Command):
    """journal organization: the domains the organization folder holds with their Roles, each Role's cardinality, whether it writes and its models, then the files that broke the schema and the version read; reload reads the folder again; plans lists per domain the plans with tasks handed to its Roles."""

    noun = "organization"
    default_verb = "list"

    def __init__(self, organization: Organization, domain_plans: DomainPlans) -> None:
        self.organization, self.domain_plans = organization, domain_plans

    def arguments(self, verbs) -> None:
        self.verb(verbs, "list", "list the domains with their Roles, the problems found in the files and the version read")
        self.verb(verbs, "reload", "read the organization folder again, then list it")
        self.verb(verbs, "plans", "list each domain's board: the plans with tasks handed to its Roles, each with only that domain's tasks, the phase it stands in there, and whether it is active: a Role of the domain works or holds one of them")

    def list(self, args: Namespace, caller: Caller) -> int:
        self.print_contracts(self.organization.contracts())
        return 0

    def reload(self, args: Namespace, caller: Caller) -> int:
        self.print_contracts(self.organization.reload())
        return 0

    def plans(self, args: Namespace, caller: Caller) -> int:
        contracts = self.organization.contracts()
        if contracts.is_empty():
            print(NO_ORGANIZATION)
        for domain in contracts.domains:
            print(f"domain {domain.id}: {domain.title}")
            print("\n".join(f"  {self.plan_line(domain_plan, domain.board)}" for domain_plan in self.domain_plans.of(domain.id)) or "  no plans")
        return 0

    @staticmethod
    def plan_line(domain_plan: DomainPlan, board: BoardPhases) -> str:
        tasks = ", ".join(f"task {task.id} {task.state}" for task in domain_plan.tasks)
        return f"plan {domain_plan.plan.id} {domain_plan.plan.title}, {board.name(domain_plan.phase())}{', active' if domain_plan.is_active() else ''}: {tasks}"

    def print_contracts(self, contracts: Contracts) -> None:
        if contracts.is_empty() and not contracts.problems:
            print(NO_ORGANIZATION)
        for domain in contracts.domains:
            print(f"domain {domain.id}: {domain.title}")
            for role in contracts.roles_of(domain.id):
                print(f"  role {role.id}: {role.cardinality}, {'writes' if role.writes else 'does not write'}, claude {role.models.claude}, codex {role.models.codex} on {role.models.effort}")
        for problem in contracts.problems:
            print(f"{problem.severity} {problem.path}: {problem.message}")
        if contracts.version:
            print(f"version {contracts.version}")
        if self.organization.is_stale():
            print("the folder has changed since it was read: journal organization reload reads it again; jobs already running keep the version they began on")
