from dataclasses import asdict

from journal.features.organization.support.domain import Domain
from journal.features.organization.support.domain_plan import DomainPlan
from journal.features.organization.support.domain_plans import DomainPlans
from journal.features.organization.support.organization import Organization
from journal.features.organization.support.role import Role
from journal.http.support.request import Request
from journal.repositories.domain_counts import DomainCounts
from journal.support.response import Response

LONG_TEXTS = ("guidance",)


class OrganizationController:
    """The agentic organization for the viewer in one answer: its domains with their Roles, the problems found in its files, the version read, each domain's board of plans and its live counts; the counts are also the rows of domain_counts, which the viewer's sync keeps current, and reload reads the folder again."""

    def __init__(self, organization: Organization, domain_plans: DomainPlans, counts: DomainCounts) -> None:
        self.organization, self.domain_plans, self.counts = organization, domain_plans, counts

    def index(self, request: Request) -> Response:
        return Response.json(self.shown(self.organization.contracts()))

    def reload(self, request: Request) -> Response:
        return Response.json(self.shown(self.organization.reload()))

    def shown(self, contracts) -> dict:
        counts = {row.name: row for row in self.counts.all_matching()}
        return {"version": contracts.version, "problems": [asdict(problem) for problem in contracts.problems],
                "domains": [self.domain(domain, contracts.roles_of(domain.id), counts.get(domain.id)) for domain in contracts.domains]}

    def domain(self, domain: Domain, roles: tuple[Role, ...], count) -> dict:
        shown = {name: value for name, value in asdict(domain).items() if name not in LONG_TEXTS}
        figures = count.roles if count else {}
        return {**shown, "roles": [self.role(role, figures.get(role.id, {})) for role in roles], "plans_active": count.plans_active if count else 0,
                "plans": [self.plan(domain_plan, domain) for domain_plan in self.domain_plans.of(domain.id)]}

    @staticmethod
    def role(role: Role, figures: dict) -> dict:
        shown = {name: value for name, value in asdict(role).items() if name not in LONG_TEXTS}
        return {**shown, "instances": figures.get("instances", 0), "queued": figures.get("queued", 0)}

    @staticmethod
    def plan(domain_plan: DomainPlan, domain: Domain) -> dict:
        phase = domain_plan.phase()
        return {"id": domain_plan.plan.id, "title": domain_plan.plan.title, "phase": phase.value, "phase_name": domain.board.name(phase),
                "active": domain_plan.is_active(), "tasks": [task.id for task in domain_plan.tasks],
                "done": sum(1 for task in domain_plan.tasks if task.is_closed())}
