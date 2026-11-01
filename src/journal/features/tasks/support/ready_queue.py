from __future__ import annotations

from datetime import datetime

from journal.features.estimates.estimates_options import EstimatesOptions
from journal.features.estimates.support.estimates_forecast import EstimatesForecast
from journal.features.estimates.support.work_in_progress import WorkInProgress
from journal.features.tasks.support.ready_order import ReadyOrder
from journal.models.plan import Plan
from journal.models.plan_mode import PlanMode
from journal.models.sprint import Sprint
from journal.models.task import Task
from journal.repositories.plans import PLAN_LINK, Plans
from journal.repositories.setting_rows import SettingRows
from journal.repositories.tasks import Tasks
from journal.support.time_source import TimeSource


class ReadyQueue:
    """Orders eligible open tasks by deadline risk, critical slack and age before priority and size, leaving organization plan tasks for their Domain seats."""

    def __init__(self, tasks: Tasks, plans: Plans, forecasts: EstimatesForecast,
                 settings: SettingRows, time_source: TimeSource, flow: WorkInProgress) -> None:
        self.tasks, self.plans, self.forecasts = tasks, plans, forecasts
        self.settings, self.time_source = settings, time_source
        self.flow = flow

    def open_tasks(self, count: int) -> list[Task]:
        available = [task for task in self.tasks.open_candidates()
                     if not self.flow.block_reason(task) and not self.is_organization_task(task)]
        return self.ordered(available)[:count]

    def is_organization_task(self, task: Task) -> bool:
        return any(plan.mode == PlanMode.ORGANIZATION for plan in self.plans.containing(task))

    def open_task(self) -> Task | None:
        return next(iter(self.open_tasks(1)), None)

    def open_ids(self, count: int) -> tuple[int, ...]:
        return tuple(task.row_id for task in self.open_tasks(count))

    def ordered(self, tasks: list[Task]) -> list[Task]:
        if self.settings.option(EstimatesOptions.MODE) == "off":
            return sorted(tasks, key=lambda task: (-task.priority, task.row_id))
        forecasts = self.task_forecasts(tasks)
        now = self.time_source.moment()
        threshold = self.settings.integer(EstimatesOptions.SPRINT_MISS_WARNING_PERCENT)
        return sorted(tasks, key=lambda task: self.rank_key(task, forecasts.get(task.row_id), now, threshold))

    def task_forecasts(self, tasks: list[Task]) -> dict[int, dict | None]:
        by_plan: dict[int, tuple[Plan, dict | None, Sprint | None]] = {}
        for task in tasks:
            for ref in self.tasks.links.targets(task, PLAN_LINK):
                if ref.id not in by_plan:
                    plan = self.plans.find(ref.id)
                    sprint = self.forecasts.forecasts.plan_sprint(plan)
                    by_plan[ref.id] = plan, self.forecasts.forecast(plan), sprint
        return {task.row_id: self.applicable_forecast(task, by_plan) for task in tasks}

    def applicable_forecast(self, task: Task, by_plan: dict[int, tuple[Plan, dict | None, Sprint | None]]) -> dict | None:
        candidates = []
        for ref in self.tasks.links.targets(task, PLAN_LINK):
            plan, forecast, sprint = by_plan[ref.id]
            ends_on = sprint.ends_on if sprint else ""
            if forecast is None and sprint is None:
                continue
            facts = forecast or {}
            candidates.append((ends_on or "9999-12-31", plan.row_id,
                               {**facts, "sprint": {"ends_on": ends_on} if sprint else None}))
        return min(candidates, default=("", 0, None))[2]

    @staticmethod
    def rank_key(task: Task, forecast: dict | None, now: datetime, threshold: int) -> tuple:
        return ReadyOrder.rank_key(task, forecast, now, threshold)

    @staticmethod
    def probability(forecast: dict | None) -> int | None:
        return ReadyOrder.probability(forecast)

    @staticmethod
    def risk_group(probability: int | None, forecast: dict | None, threshold: int) -> tuple[int, int, str]:
        return ReadyOrder.risk_group(probability, forecast, threshold)

    @staticmethod
    def slack(task_id: int, forecast: dict | None) -> int | None:
        return ReadyOrder.slack(task_id, forecast)
