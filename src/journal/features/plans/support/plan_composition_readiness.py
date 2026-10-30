from journal.features.estimates.estimates_options import ENFORCEMENT_PLAN_BOUNDARY, EstimatesOptions
from journal.features.estimates.support.task_size_scale import TaskSizeScale
from journal.features.organization.support.organization import Organization
from journal.models.plan import Plan
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

    def validate(self, plan: Plan) -> None:
        if not self.is_new_enforced_plan(plan):
            return
        scale = self.scale.values()
        contracts = self.organization.contracts()
        for task in self.plans.plan_tasks(plan):
            self.require_size(task, scale)
            self.require_domain(plan, task, contracts)
        self.dependencies.validate_plan(plan)

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
        raise Rejection(f"task {task.row_id} has no approved story point size: set it with `journal task size {task.row_id} <points> --reason \"why this size fits\"` from estimates.size_scale")

    def require_domain(self, plan: Plan, task, contracts) -> None:
        name = self.domains.planned_domain_name(task)
        if not name:
            raise Rejection(f"task {task.row_id} has no accountable planned domain: set one on its task page or add it with `journal plan add {plan.row_id} \"<task>\" --domain <domain> --size <points>`")
        domain = contracts.domain(name)
        if domain is None:
            raise Rejection(f"task {task.row_id} names planned domain {name}, which is not in the loaded organization contract: correct its domain in domain.toml and reload the organization")
        if not any(item.strip() for item in domain.responsible):
            raise Rejection(f"planned domain {name} has no accountable responsibility: add a responsible entry to its domain.toml")
        done = domain.definition_of_done
        if done is None or not done.criterion.strip() or not done.target.strip():
            raise Rejection(f"planned domain {name} has no definition of done: add [definition_of_done] with criterion, evidence and target to its domain.toml")
