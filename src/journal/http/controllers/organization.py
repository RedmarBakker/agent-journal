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
    """The viewer's organization data: source path and commit, domains with their Roles and live counts, contract problems and plan boards; a Role detail keeps its full contract and guidance for the side panel."""

    def __init__(self, organization: Organization, domain_plans: DomainPlans, counts: DomainCounts) -> None:
        self.organization, self.domain_plans, self.counts = organization, domain_plans, counts

    def index(self, request: Request) -> Response:
        return Response.json(self.shown(self.organization.contracts()))

    def reload(self, request: Request) -> Response:
        return Response.json(self.shown(self.organization.reload()))

    def shown(self, contracts) -> dict:
        counts = {row.name: row for row in self.counts.all_matching()}
        return {"folder": contracts.folder, "commit": contracts.commit, "version": contracts.version, "problems": [asdict(problem) for problem in contracts.problems],
                "domains": [self.domain(domain, contracts.roles_of(domain.id), counts.get(domain.id)) for domain in contracts.domains]}

    def role_contract(self, request: Request) -> Response:
        domain_id, role_id = request.params["domain"], request.params["role"]
        role = next((role for role in self.organization.contracts().roles if role.domain == domain_id and role.id == role_id), None)
        return Response.json(asdict(role)) if role else Response.absent(f"no Role {role_id} in domain {domain_id}")

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
