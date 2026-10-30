from argparse import Namespace
import json

from journal.console.command import Command
from journal.features.organization.support.board_phases import BoardPhases
from journal.features.organization.support.domain_plan import DomainPlan
from journal.features.organization.support.domain_plans import DomainPlans
from journal.features.organization.support.hub_traffic_audit import HubTrafficAudit
from journal.features.organization.support.organization import Organization
from journal.features.organization.support.organization_hub import OrganizationHub
from journal.features.organization.support.contracts import Contracts
from journal.support.caller import Caller

NO_ORGANIZATION = "no organization: set the agentic organization folder on the Settings page"


class OrganizationCommand(Command):
    """journal organization: list the organization's domains and Roles; reload their contracts; list domain plans; audit OpenRig queue traffic against each seat's hub routes."""

    noun = "organization"
    default_verb = "list"

    def __init__(self, organization: Organization, domain_plans: DomainPlans, traffic: HubTrafficAudit, hub: OrganizationHub) -> None:
        self.organization, self.domain_plans, self.traffic, self.hub = organization, domain_plans, traffic, hub

    def arguments(self, verbs) -> None:
        self.verb(verbs, "list", "list the domains with their Roles, the problems found in the files and the version read")
        self.verb(verbs, "reload", "read the organization folder again, then list it")
        self.verb(verbs, "plans", "list each domain's board: the plans with tasks handed to its Roles, each with only that domain's tasks, the phase it stands in there, and whether it is active: a Role of the domain works or holds one of them")
        self.verb(verbs, "audit", "list OpenRig queue items that route around their organization's hub, with the recorded actor and identity provenance")
        handoff = self.verb(verbs, "handoff", "hand a task to the next seat along the organization's hub routes")
        handoff.add_argument("task", type=int)
        handoff.add_argument("target", help="domain:<id> or role:<domain>/<role>")
        self.verb(verbs, "inbox", "read tasks handed to this generated organization seat")

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

    def audit(self, args: Namespace, caller: Caller) -> int:
        findings = self.traffic.findings()
        if not findings:
            print("no hub-skipping queue traffic")
        for finding in findings:
            provenance = finding.identity_provenance
            if isinstance(provenance, (dict, list)):
                provenance = json.dumps(provenance, sort_keys=True)
            print(f"hub-skipping queue item {finding.item_id}: {finding.source} -> {finding.destination}; actor session {finding.actor_session or 'not reported'}; identity provenance {provenance or 'not reported'}")
        return 0

    def handoff(self, args: Namespace, caller: Caller) -> int:
        self.hub.handoff(args.task, args.target, caller)
        return 0

    def inbox(self, args: Namespace, caller: Caller) -> int:
        self.hub.inbox(caller)
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
