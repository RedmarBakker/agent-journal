from journal.engine.support.lazy_facts import LazyFacts
from journal.features.estimates.support.baseline_forecast import BaselineForecast
from journal.features.estimates.support.estimates_forecast import EstimatesForecast
from journal.features.estimates.support.estimates_risk_data import EstimatesRiskData
from journal.features.estimates.support.work_in_progress import WorkInProgress
from journal.models.agent import Agent
from journal.models.plan import Plan
from journal.repositories.plans import Plans
from journal.repositories.scope import Scope
from journal.repositories.task_dependencies import TaskDependencies
from journal.repositories.task_outcomes import TaskOutcomes
from journal.repositories.task_sizes import TaskSizes
from journal.support.stage_times import StageTimes


class EstimatesDataReader:
    """Reads current plan risk facts for the estimates conduct."""

    def __init__(self, plans: Plans, scope: Scope, forecasts: EstimatesForecast, dependencies: TaskDependencies,
                 sizes: TaskSizes, outcomes: TaskOutcomes, stages: StageTimes, flow: WorkInProgress) -> None:
        self.plans, self.scope, self.forecasts, self.dependencies = plans, scope, forecasts, dependencies
        self.sizes, self.outcomes, self.stages, self.flow = sizes, outcomes, stages, flow

    def read(self, agent: Agent) -> LazyFacts:
        return LazyFacts("estimates", {"risk": self.risk},
                         lambda: self.scope.environment(agent.environment_id), self.stages)

    def risk(self) -> EstimatesRiskData:
        plan = self.active_plan()
        if plan is None:
            return EstimatesRiskData()
        forecast, history = self.forecasts.analysis(plan)
        current = self.current_task(plan)
        aging = self.aging(plan, current, history)
        growth_points, growth = self.scope_growth(plan)
        following = self.plans.following_task(plan)
        wip_advice = self.flow.block_reason(following) if following is not None else ""
        sprint = forecast.get("sprint") if forecast else None
        return EstimatesRiskData(plan.row_id, self.forecasts.basis(forecast), growth_points, growth,
                                 *aging, self.critical_prerequisites(plan), sprint["ends_on"] if sprint else "",
                                 forecast.get("probability_this_sprint") if forecast else None,
                                 forecast.get("p85") or "" if forecast else "",
                                 self.critical_path_advice(forecast), wip_advice)

    def active_plan(self) -> Plan | None:
        plan = next(iter(self.plans.running_plans()), None)
        if plan is not None:
            return plan
        reference = next((ref for ref in self.scope.bound() if ref.type == Plan.table()), None)
        return next(iter(self.plans.global_matching(id=reference.id)), None) if reference else None

    def current_task(self, plan: Plan):
        return next((task for task in self.plans.plan_tasks(plan) if task.is_started()), None)

    def scope_growth(self, plan: Plan) -> tuple[int, str]:
        changes = []
        tasks = self.plans.plan_tasks(plan)
        estimates = {task.row_id: self.sizes.show(task.row_id) for task in tasks}
        if not any(any(row["change_type"] == "first_ready" for row in estimate["history"]) for estimate in estimates.values()):
            return 0, ""
        for task in tasks:
            estimate = estimates[task.row_id]
            current = estimate["current_size"] or 0
            first_ready = estimate["first_ready_size"]
            if first_ready is None:
                if any(row["change_type"] == "first_ready" for row in estimate["history"]):
                    continue
                baseline = 0
            else:
                baseline = first_ready
            added = max(0, current - baseline)
            if added:
                changes.append((task.row_id, added))
        points = sum(value for _task_id, value in changes)
        summary = ", ".join(f"task {task_id} +{value}" for task_id, value in changes)
        return points, f"{points} story points ({summary})" if points else ""

    def aging(self, plan: Plan, current, history: dict | None) -> tuple[int, float, float, int]:
        if current is None or history is None:
            return 0, 0.0, 0.0, 0
        current_summary = self.outcomes.summary(current.row_id)
        active_seconds = current_summary["active_seconds"] or 0.0
        current_history = next((row for row in history["tasks"] if row["task_id"] == current.row_id), None)
        cohort = next((row["cohort_key"] for row in reversed(current_history["outcomes"]) if row["cohort_key"]), None) if current_history else None
        if not cohort:
            return 0, active_seconds, 0.0, 0
        durations = [row["execution"]["active_seconds"] for row in history["tasks"]
                    if row["task_id"] != current.row_id and row["execution"]["execution_status"] == "completed"
                    and row["execution"]["active_seconds"] is not None
                    and any(outcome["cohort_key"] == cohort for outcome in row["outcomes"])]
        p85 = BaselineForecast.percentile(durations, 0.85) if durations else None
        if p85 is None:
            return 0, active_seconds, 0.0, 0
        return current.row_id, active_seconds, float(p85), len(durations)

    def critical_prerequisites(self, plan: Plan) -> tuple[tuple[int, int], ...]:
        edges = self.dependencies.show(plan)["edges"]
        return tuple((edge["task_id"], edge["prerequisite_id"]) for edge in edges
                     if not self.plans.tasks.find(edge["task_id"]).is_closed()
                     and not self.plans.tasks.find(edge["prerequisite_id"]).is_closed())

    @staticmethod
    def critical_path_advice(forecast: dict | None) -> str:
        path = forecast.get("critical_path", {}) if forecast else {}
        critical = path.get("critical_task_ids", ())
        if path.get("status") == "estimated" and critical:
            return "critical tasks " + ", ".join(f"#{task_id}" for task_id in critical)
        independent = [task_id for group in path.get("independent_groups", ()) for task_id in group]
        return "independent tasks " + ", ".join(f"#{task_id}" for task_id in independent) if independent else ""
