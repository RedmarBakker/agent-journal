from datetime import datetime, timezone

from journal.features.estimates.estimates_options import EstimatesOptions
from journal.features.estimates.support.estimates_forecast import EstimatesForecast
from journal.features.estimates.support.work_in_progress import WorkInProgress
from journal.models.plan import Plan
from journal.models.sprint import Sprint
from journal.models.task import Task
from journal.repositories.plans import PLAN_LINK, Plans
from journal.repositories.setting_rows import SettingRows
from journal.repositories.tasks import Tasks
from journal.support.time_source import TimeSource


class ReadyQueue:
    """Orders eligible open tasks by deadline risk, critical slack and age before priority and size."""

    def __init__(self, tasks: Tasks, plans: Plans, forecasts: EstimatesForecast,
                 settings: SettingRows, time_source: TimeSource, flow: WorkInProgress) -> None:
        self.tasks, self.plans, self.forecasts = tasks, plans, forecasts
        self.settings, self.time_source = settings, time_source
        self.flow = flow

    def open_tasks(self, count: int) -> list[Task]:
        available = [task for task in self.tasks.open_candidates() if not self.flow.block_reason(task)]
        return self.ordered(available)[:count]

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
        created = task.created_at or datetime.min.replace(tzinfo=timezone.utc)
        if created.tzinfo is None:
            created = created.replace(tzinfo=timezone.utc)
        local_now = now if now.tzinfo else now.replace(tzinfo=timezone.utc)
        age_days = max(0, (local_now.date() - created.astimezone(local_now.tzinfo).date()).days)
        probability = ReadyQueue.probability(forecast)
        risk = ReadyQueue.risk_group(probability, forecast, threshold)
        slack = ReadyQueue.slack(task.row_id, forecast)
        return (*risk, slack is None, slack if slack is not None else 0, -age_days,
                -task.priority, task.size is None, task.size if task.size is not None else 0,
                created.timestamp(), task.row_id)

    @staticmethod
    def probability(forecast: dict | None) -> int | None:
        probability = forecast.get("probability_this_sprint") if forecast else None
        return probability if isinstance(probability, int) and not isinstance(probability, bool) else None

    @staticmethod
    def risk_group(probability: int | None, forecast: dict | None, threshold: int) -> tuple[int, int, str]:
        sprint = forecast.get("sprint") if forecast else None
        ends_on = sprint.get("ends_on", "") if isinstance(sprint, dict) else ""
        if not ends_on or probability is None:
            return 1, 0, ends_on or "9999-12-31"
        return (0 if probability < threshold else 2), probability, ends_on

    @staticmethod
    def slack(task_id: int, forecast: dict | None) -> int | None:
        path = forecast.get("critical_path", {}) if forecast else {}
        task = next((row for row in path.get("tasks", ()) if row.get("task_id") == task_id), None)
        slack = task.get("slack_days") if task else None
        return slack if isinstance(slack, int) and not isinstance(slack, bool) else None
