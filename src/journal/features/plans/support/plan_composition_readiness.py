from journal.features.estimates.estimates_options import ENFORCEMENT_PLAN_BOUNDARY, EstimatesOptions
from journal.features.estimates.support.task_size_scale import TaskSizeScale
from journal.features.organization.support.organization import Organization
from journal.models.plan import Plan
from journal.models.plan_mode import PlanMode
from journal.repositories.domain_rows import DomainRows
from journal.repositories.plans import Plans
from journal.repositories.setting_rows import SettingRows
from journal.repositories.task_dependencies import TaskDependencies
from journal.support.rejection import Rejection


class PlanCompositionReadiness:
    """Checks newly composed plans against the active sizing and delivery contracts."""

    def __init__(self, settings: SettingRows, scale: TaskSizeScale, plans: Plans, domains: DomainRows,
                 organization: Organization, dependencies: TaskDependencies) -> None:
        self.settings, self.scale, self.plans, self.domains = settings, scale, plans, domains
        self.organization, self.dependencies = organization, dependencies

    def validate(self, plan: Plan) -> tuple[str, ...]:
        contracts = self.organization.contracts()
        self.require_organization_mode(plan, contracts.folder)
        tasks = self.plans.plan_tasks(plan)
        definitions: dict[str, str] = {}
        if plan.mode == PlanMode.ORGANIZATION:
            for task in tasks:
                name = self.domains.planned_domain_name(task)
                if name not in definitions:
                    definitions[name] = self.require_domain(plan, task, contracts)
        if not self.is_new_enforced_plan(plan):
            return tuple(definitions.values())
        scale = self.scale.values()
        for task in tasks:
            self.require_size(task, scale)
        self.dependencies.validate_plan(plan)
        return tuple(definitions.values())

    @staticmethod
    def require_organization_mode(plan: Plan, folder: str) -> None:
        if folder and plan.mode == PlanMode.SOLO and not plan.mode_chosen:
            raise Rejection(
                f"plan {plan.id} needs a mode: `journal plan mode {plan.id} solo` or organization"
            )

    def is_new_enforced_plan(self, plan: Plan) -> bool:
        setting = next((row for row in self.settings.project_rows() if row.key == EstimatesOptions.MODE.key), None)
        if setting is None or setting.value != "enforce":
            return False
        boundary = self.settings.project(ENFORCEMENT_PLAN_BOUNDARY)
        if isinstance(boundary, int) and not isinstance(boundary, bool):
            return plan.row_id > boundary
        if plan.created_at is None:
            return False
        enabled_at = setting.updated_at or setting.created_at
        return enabled_at is not None and plan.created_at > enabled_at

    @staticmethod
    def require_size(task, scale: tuple[int, ...]) -> None:
        if task.size in scale:
            return
        raise Rejection(f"task {task.row_id}: use estimates.size_scale; `journal task size {task.row_id} <points> --reason <why>`")

    def require_domain(self, plan: Plan, task, contracts) -> str:
        name = self.domains.planned_domain_name(task)
        if not name:
            raise Rejection(f"task {task.row_id} needs a domain: edit its task page or use `journal plan add {plan.row_id} --domain <name>`")
        domain = contracts.domain(name)
        if domain is None:
            raise Rejection(f"task {task.row_id} names unknown domain {name}: fix domain.toml and reload the organization")
        if not any(item.strip() for item in domain.responsible):
            raise Rejection(f"planned domain {name} needs a responsible role in domain.toml")
        done, defaulted = contracts.definition_of_done_for(domain)
        if not done.criterion.strip() or not done.target.strip():
            raise Rejection(f"domain {name}: set its definition in domain.toml or omit it for the organization default")
        source = "the organization default" if defaulted else "domain.toml"
        return f"domain {name} uses {source} definition of done: {done.criterion} ({done.evidence.value}; target: {done.target})"
