from journal.features.estimates.estimates_options import EstimatesOptions, wip_limit
from journal.models.plan import Plan
from journal.models.plan_state import PlanState
from journal.models.task import Task
from journal.models.task_state import TaskState
from journal.repositories.delivery_records import DeliveryRecords
from journal.repositories.plans import PLAN_LINK, Plans
from journal.repositories.scope import Scope
from journal.repositories.setting_rows import SettingRows
from journal.repositories.tasks import FINISHED_LINK, Tasks, WORKERS
from journal.support.rejection import Rejection


class WorkInProgress:
    """Reads overlapping execution and delivery work and refuses only new work beyond owner limits."""

    def __init__(self, tasks: Tasks, plans: Plans, delivery: DeliveryRecords, settings: SettingRows, scope: Scope) -> None:
        self.tasks, self.plans, self.delivery, self.settings, self.scope = tasks, plans, delivery, settings, scope

    def plan(self, plan_id: int) -> dict:
        plan = self.plans.find(plan_id)
        tasks = self.plans.plan_tasks(plan)
        execution = [task for task in tasks if self.execution(task)]
        delivery = [task.row_id for task, _data in self.delivery_tasks(plan)]
        backlog = [task.row_id for task in tasks if task.state == TaskState.BLOCKED and task.started_at is None]
        seats = {holder.id for task in execution if (holder := self.tasks.holder(task)) is not None
                 and holder.type == WORKERS}
        return {"execution_wip_task_ids": [task.row_id for task in execution],
                "delivery_wip_task_ids": delivery, "blocked_backlog_task_ids": backlog,
                "occupied_execution_seats": len(seats), "wip_total": None}

    def task(self, task_id: int) -> dict:
        task = self.tasks.find(task_id)
        return {"task_id": task.row_id, "execution_wip": self.execution(task),
                "stage": self.stage(task), "delivery_wip": self.delivery_wip(task), "combined_wip": None}

    def delivery_wip(self, task: Task) -> bool:
        if task.started_at is None or task.state == TaskState.CANCELLED:
            return False
        plans = self.task_plans(task)
        return not plans or any(self.delivery.task_data(plan, task, self.delivery.plan_records(plan))["status"] != "delivered"
                                for plan in plans)

    def task_plans(self, task: Task) -> list[Plan]:
        return [plan for ref in self.tasks.links.targets(task, PLAN_LINK) if ref.type == Plan.table()
                if (plan := self.plans.find(ref.id)).state != PlanState.CANCELLED]

    def require_start(self, task: Task) -> None:
        reason = self.block_reason(task)
        if reason:
            raise Rejection(reason)

    def block_reason(self, task: Task) -> str:
        if self.mode() != "enforce" or task.started_at is not None:
            return ""
        execution_limit = wip_limit(self.settings.option(EstimatesOptions.EXECUTION_WIP_LIMIT), EstimatesOptions.EXECUTION_WIP_LIMIT.key)
        if execution_limit and len(self.execution_tasks()) >= execution_limit:
            return self.execution_limit_message(task, execution_limit)
        for plan in self.task_plans(task):
            block = self.plan_delivery_block(task, plan, limits)
            if block:
                return block
        return ""

    def execution_tasks(self) -> list[Task]:
        return [task for task in self.tasks.selected_globally(self.tasks.query().order("id")) if self.execution(task)]

    def execution(self, task: Task) -> bool:
        if task.state == TaskState.CANCELLED or task.started_at is None:
            return False
        if task.state != TaskState.COMPLETED:
            return True
        return bool(self.tasks.links.sources(task, FINISHED_LINK))

    def stage(self, task: Task) -> str:
        if self.tasks.links.sources(task, FINISHED_LINK):
            return "finished unmerged"
        return task.state.value

    def plan_delivery_block(self, candidate: Task, plan: Plan, limits: dict) -> str:
        pending = self.delivery_tasks(plan)
        plan_limit = wip_limit(self.settings.option(EstimatesOptions.PLAN_DELIVERY_WIP_LIMIT), EstimatesOptions.PLAN_DELIVERY_WIP_LIMIT.key)
        if plan_limit and len(pending) >= plan_limit:
            task, data = pending[0]
            return self.delivery_limit_message("plan", plan_limit, task, data, candidate)
        domain_limit = wip_limit(self.settings.option(EstimatesOptions.DOMAIN_DELIVERY_WIP_LIMIT), EstimatesOptions.DOMAIN_DELIVERY_WIP_LIMIT.key)
        candidate_data = self.delivery.task_data(plan, candidate, self.delivery.plan_records(plan))
        domain = candidate_data.get("domain")
        domain_tasks = self.domain_delivery_tasks(domain) if domain and domain_limit else []
        if domain_tasks and len(domain_tasks) >= domain_limit:
            task, data = domain_tasks[0]
            return self.delivery_limit_message(domain, domain_limit, task, data, candidate)
        return ""

    def delivery_tasks(self, plan: Plan) -> list[tuple[Task, dict]]:
        tasks = self.plans.plan_tasks(plan)
        records = self.delivery.plan_records(plan)
        return [(task, data) for task in tasks if task.started_at is not None and task.state != TaskState.CANCELLED
                and (data := self.delivery.task_data(plan, task, records))["status"] != "delivered"]

    def domain_delivery_tasks(self, domain: str) -> list[tuple[Task, dict]]:
        rows = []
        seen = set()
        for plan in self.plans.selected_globally(self.plans.query().order("id")):
            if plan.state == PlanState.CANCELLED:
                continue
            with self.scope.environment(plan.environment_id):
                for task, data in self.delivery_tasks(plan):
                    if data.get("domain") == domain and task.row_id not in seen:
                        seen.add(task.row_id)
                        rows.append((task, data))
        return rows

    def execution_limit_message(self, candidate: Task, limit: int) -> str:
        blocker = self.execution_tasks()[0]
        if blocker.state == TaskState.TESTING:
            resolution = f"finish testing task {blocker.id}"
        elif blocker.state == TaskState.COMPLETED:
            resolution = f"merge the finished work for task {blocker.id}"
        elif blocker.state in (TaskState.PAUSED, TaskState.BLOCKED):
            resolution = f"resolve its wait, then finish task {blocker.id}"
        else:
            resolution = f"finish task {blocker.id}"
        return f"project execution WIP limit {limit} is full: task {blocker.id} is {self.stage(blocker)}; {resolution} before starting task {candidate.id}"

    @staticmethod
    def delivery_limit_message(scope: str, limit: int, task: Task, data: dict, candidate: Task) -> str:
        if data["status"] == "awaiting_deployment":
            resolution = "the owner can accept the pending domain delivery after successful production deployment evidence is available"
        elif data["status"] == "awaiting_merge":
            resolution = f"merge task {task.id} before its owner accepts domain delivery"
        elif data["status"] == "awaiting_evidence":
            resolution = "the owner can accept the pending domain delivery after its required evidence is available"
        else:
            resolution = f"complete and merge task {task.id}, then ask its owner to accept the pending domain delivery"
        return f"{scope} delivery WIP limit {limit} is full: task {task.id} is {data['status']}; {resolution} before starting task {candidate.id}"

    def mode(self) -> str:
        return str(self.settings.option(EstimatesOptions.MODE))

