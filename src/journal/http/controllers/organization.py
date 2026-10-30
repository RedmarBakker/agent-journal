from dataclasses import asdict

from journal.features.organization.support.caps import Caps
from journal.features.organization.support.domain import Domain
from journal.features.organization.support.domain_plan import DomainPlan
from journal.features.organization.support.domain_plans import DomainPlans
from journal.features.organization.support.organization import Organization
from journal.features.organization.support.role import Role
from journal.features.organization.support.usage_ledger import UsageEstimate, UsageLedger
from journal.features.plans.jobs.template_plan_start import TemplatePlanStart
from journal.features.plans.support.plan_agents import PlanAgents
from journal.http.support.request import Request
from journal.models.environment import Environment
from journal.models.plan import Plan
from journal.models.plan_state import PlanState
from journal.models.question import Question
from journal.models.support.ref import Ref
from journal.models.task import Task
from journal.models.template import Template
from journal.repositories.domain_counts import DomainCounts
from journal.repositories.domain_rows import DomainRows
from journal.repositories.delivery_forecasts import DeliveryForecasts
from journal.repositories.plans import Plans
from journal.repositories.tasks import Tasks
from journal.repositories.templates import Templates
from journal.support.response import Response
from journal.support.time_source import TimeSource

LONG_TEXTS = ("guidance",)


class OrganizationController:
    """The viewer's organization data: source path and commit, domains with their Roles and live counts, contract problems and plan boards; a Role detail keeps its full contract and guidance for the side panel."""

    def __init__(self, organization: Organization, domain_plans: DomainPlans, counts: DomainCounts, usage: UsageLedger,
                 time_source: TimeSource, plans: Plans, tasks: Tasks, domain_rows: DomainRows, plan_agents: PlanAgents,
                 caps: Caps, templates: Templates, template_start: TemplatePlanStart, forecasts: DeliveryForecasts) -> None:
        self.organization, self.domain_plans, self.counts = organization, domain_plans, counts
        self.usage, self.time_source = usage, time_source
        self.plans, self.tasks, self.domain_rows = plans, tasks, domain_rows
        self.plan_agents, self.caps, self.templates, self.template_start = plan_agents, caps, templates, template_start
        self.forecasts = forecasts

    def index(self, request: Request) -> Response:
        return Response.json(self.shown(self.organization.contracts(), request.actor))

    def reload(self, request: Request) -> Response:
        return Response.json(self.shown(self.organization.reload(), request.actor))

    def shown(self, contracts, actor) -> dict:
        counts = {row.name: row for row in self.counts.all_matching()}
        domain_plans = {domain.id: self.domain_plans.of(domain.id) for domain in contracts.domains}
        all_plans = self.plans.all()
        known_plans = {plan.id: plan for plan in all_plans}
        known_plans.update({planned.plan.id: planned.plan for plans in domain_plans.values() for planned in plans})
        estimates = self.usage.estimates(known_plans, self.time_source.seconds())
        summaries = {plan_id: self.plan(plan, estimates[plan_id]) for plan_id, plan in known_plans.items()}
        return {"folder": contracts.folder, "commit": contracts.commit, "version": contracts.version, "problems": [asdict(problem) for problem in contracts.problems],
                "plans": [summaries[plan.id] for plan in all_plans], "scheduled_plans": self.scheduled_plans(),
                "sprint_forecasts": self.forecasts.organization(actor),
                "domains": [self.domain(domain, contracts.roles_of(domain.id), counts.get(domain.id), domain_plans[domain.id], summaries) for domain in contracts.domains]}

    def role_contract(self, request: Request) -> Response:
        domain_id, role_id = request.params["domain"], request.params["role"]
        role = next((role for role in self.organization.contracts().roles if role.domain == domain_id and role.id == role_id), None)
        return Response.json(asdict(role)) if role else Response.absent(f"no Role {role_id} in domain {domain_id}")

    def domain(self, domain: Domain, roles: tuple[Role, ...], count, plans: tuple[DomainPlan, ...], summaries: dict[int, dict]) -> dict:
        shown = {name: value for name, value in asdict(domain).items() if name not in LONG_TEXTS}
        figures = count.roles if count else {}
        return {**shown, "roles": [self.role(role, figures.get(role.id, {})) for role in roles], "plans_active": count.plans_active if count else 0,
                "plans": [self.domain_plan(domain_plan, domain, summaries[domain_plan.plan.id]) for domain_plan in plans]}

    @staticmethod
    def role(role: Role, figures: dict) -> dict:
        shown = {name: value for name, value in asdict(role).items() if name not in LONG_TEXTS}
        return {**shown, "instances": figures.get("instances", 0), "queued": figures.get("queued", 0)}

    def plan(self, plan: Plan, estimate: UsageEstimate) -> dict:
        tasks = self.plans.plan_tasks(plan)
        overall = DomainPlan(plan, tuple(tasks), self.domain_rows.reviewed_ids(tasks))
        waiting_refs = self.waiting_refs(plan, tasks)
        environment = self.plan_agents.environment(plan)
        return {"id": plan.id, "title": plan.title, "phase": overall.phase().value, "mode": plan.mode.value,
                "state": plan.state.value, "active": overall.is_active(), "tasks": [task.id for task in tasks],
                "done": overall.done_count(), "story_points": self.story_points(tasks),
                "waits_on": self.waits_on(plan, overall, waiting_refs),
                "waiting_on_you": self.waiting_on_you(plan, waiting_refs),
                "plan_agent_state": self.plan_agent_state(environment), "chat": environment.name if environment else "",
                "estimated_api_cost_usd": estimate.amount_usd, "estimated_api_cost_status": estimate.status,
                "cost_cap_usd": self.caps.plan_cost(estimate).limit}

    @staticmethod
    def story_points(tasks: list[Task]) -> dict:
        sized = [task for task in tasks if isinstance(task.size, int) and not isinstance(task.size, bool) and task.size > 0]
        done = [task for task in sized if task.state.value == "completed"]
        unknown = len(tasks) - len(sized)
        return {"total": sum(task.size for task in sized) if sized else None,
                "done": sum(task.size for task in done) if done else None,
                "sized_tasks": len(sized), "unknown_tasks": unknown}

    def waiting_refs(self, plan: Plan, tasks: list[Task]) -> list[Ref]:
        task_refs = [ref for refs in self.tasks.open_wait_refs(tasks).values() for ref in refs]
        return [*self.tasks.open_waits(plan), *task_refs]

    @staticmethod
    def waiting_on_you(plan: Plan, waiting_refs: list[Ref]) -> bool:
        return plan.state == PlanState.READY or any(ref.type == Question.table() for ref in waiting_refs)

    @staticmethod
    def waits_on(plan: Plan, overall: DomainPlan, waiting_refs: list[Ref]) -> str:
        if (plan.state not in (PlanState.READY, PlanState.REVIEWING) and not plan.is_blocked()
                and any(ref.type == Question.table() for ref in waiting_refs)):
            return "your answer"
        return overall.waits_on()

    def plan_agent_state(self, environment: Environment | None) -> str:
        if environment is None:
            return "not started"
        return "running" if self.plan_agents.is_running(environment) else "stopped"

    def scheduled_plans(self) -> list[dict]:
        return [self.scheduled_plan(template) for template in self.templates.scheduled()]

    def scheduled_plan(self, template: Template) -> dict:
        next_start = template.schedule.next_start(self.template_start.last_start(template), self.time_source.moment())
        return {"id": template.id, "title": template.title, "schedule": template.schedule.value, "next_start": next_start.isoformat()}

    @staticmethod
    def domain_plan(domain_plan: DomainPlan, domain: Domain, summary: dict) -> dict:
        phase = domain_plan.phase()
        return {**summary, "phase": phase.value, "phase_name": domain.board.name(phase), "active": domain_plan.is_active(),
                "tasks": [task.id for task in domain_plan.tasks], "done": domain_plan.done_count(), "waits_on": domain_plan.waits_on()}
