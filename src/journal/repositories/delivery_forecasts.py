from datetime import datetime, timezone
from zoneinfo import ZoneInfo

from journal.features.estimates.estimates_options import EstimatesOptions
from journal.features.estimates.support.baseline_forecast import BaselineForecast
from journal.models.plan import Plan
from journal.models.sprint import Sprint
from journal.models.sprint_state import SprintState
from journal.repositories.forecast_snapshots import ForecastSnapshots
from journal.repositories.plan_outcome_history import PlanOutcomeHistory
from journal.repositories.sprint_outcome_metrics import SprintOutcomeMetrics
from journal.repositories.sprints import SPRINT_PLAN, Sprints
from journal.repositories.setting_rows import SettingRows
from journal.support.actor import Actor
from journal.support.time_source import TimeSource


class DeliveryForecasts:
    """The owner-scoped baseline forecast assembled from sprint and delivery history."""

    def __init__(self, sprints: Sprints, metrics: SprintOutcomeMetrics, history: PlanOutcomeHistory,
                 calculator: BaselineForecast, snapshots: ForecastSnapshots, settings: SettingRows,
                 time_source: TimeSource) -> None:
        self.sprints, self.metrics, self.history = sprints, metrics, history
        self.calculator, self.snapshots, self.settings, self.time_source = calculator, snapshots, settings, time_source

    def sprint(self, sprint_id: int, actor: Actor) -> dict:
        sprint, source, forecast = self.sprint_read(sprint_id, actor)
        return self.snapshots.capture(sprint, source, forecast, actor)

    def organization(self, actor: Actor) -> list[dict]:
        sprints = self.sprints.index(actor)
        reports = [self.metrics.read(sprint["id"], actor) for sprint in sprints]
        reports_by_id = {report["sprint"]["id"]: report for report in reports}
        histories = self.plan_histories_for(sprints, actor)
        rows = []
        for summary in sprints:
            sprint = self.sprints.find(summary["id"])
            source = self.source_from(reports_by_id[summary["id"]], reports, histories)
            forecast = self.calculator.estimate(source)
            forecast = self.sprint_forecast(forecast, source, summary, histories)
            rows.append({"sprint": summary, "forecast": self.snapshots.capture(sprint, source, forecast, actor)})
        return rows

    def plan(self, plan_id: int, actor: Actor) -> dict:
        plan, source, forecast = self.plan_projection(plan_id, actor)
        return self.snapshots.capture(plan, source, forecast, actor)

    def estimate_plan(self, plan_id: int, actor: Actor) -> dict:
        return self.plan_projection(plan_id, actor)[2]

    def plan_projection(self, plan_id: int, actor: Actor) -> tuple[Plan, dict, dict]:
        history = self.history.read(plan_id, actor)
        plan = self.history.plans.find(plan_id)
        source, forecast = self.plan_forecast(plan, history, actor)
        return plan, source, forecast

    def estimate_from_history(self, plan: Plan, history: dict, actor: Actor) -> dict:
        return self.plan_forecast(plan, history, actor)[1]

    def plan_forecast(self, plan: Plan, history: dict, actor: Actor) -> tuple[dict, dict]:
        sprint = self.plan_sprint(plan)
        if sprint:
            _sprint, source, shared = self.sprint_read(sprint.row_id, actor)
            forecast = self.plan_result(shared, plan_id, source)
        else:
            source = self.plan_source(plan, history, actor)
            forecast = self.calculator.estimate(source)
            forecast = {**forecast, **self.capacity_freshness(forecast, source)}
        forecast = {**forecast, **self.delivery_summary(history),
                    "sprint": self.sprints.summary(sprint) if sprint else None}
        return source, forecast

    def sprint_read(self, sprint_id: int, actor: Actor) -> tuple[Sprint, dict, dict]:
        report = self.metrics.read(sprint_id, actor)
        source, histories = self.source(report, actor)
        sprint = self.sprints.find(sprint_id)
        forecast = self.calculator.estimate(source)
        forecast = self.sprint_forecast(forecast, source, self.sprints.summary(sprint), histories)
        return sprint, source, forecast

    def source(self, current: dict, actor: Actor) -> tuple[dict, list[dict]]:
        reports = [current, *(self.metrics.read(row["id"], actor) for row in self.sprints.index(actor)
                              if row["id"] != current["sprint"]["id"])]
        plans = self.plan_histories(actor)
        return self.source_from(current, reports, plans), plans

    def source_from(self, current: dict, reports: list[dict], plans: list[dict]) -> dict:
        batches = self.delivery_batches(plans, current["sprint"]["timezone"])
        capacity_days = self.capacity_days(reports, batches)
        scope = self.sprint_scope(current, plans)
        sprint = current["sprint"]
        return self.request(scope, reports, current["data_quality"], capacity_days, sprint, plans)

    def plan_source(self, plan: Plan, history: dict, actor: Actor) -> dict:
        reports = [self.metrics.read(row["id"], actor) for row in self.sprints.index(actor)]
        plans = self.plan_histories(actor, plan.row_id)
        timezone_name = self.timezone(reports)
        batches = self.delivery_batches(plans, timezone_name)
        capacity_days = self.capacity_days(reports, batches)
        scope = [self.history_task(plan.row_id, row) for row in history["tasks"] if row["current_in_plan"]]
        approved = self.approved(history["scope"]["plan_state"])
        for row in scope:
            row["approved_scope"] = approved
        return self.request(scope, reports, history["data_quality"], capacity_days, None, plans)

    def request(self, scope: list[dict], reports: list[dict], quality: dict, capacity_days: list[dict],
                sprint: dict | None, histories: list[dict]) -> dict:
        timezone_name = sprint["timezone"] if sprint else self.timezone(reports)
        now = self.time_source.moment().astimezone(ZoneInfo(timezone_name)).date()
        calendar = {"current_end": sprint["ends_on"] if sprint else None,
                    "next_end": self.next_end(sprint, reports) if sprint else None,
                    "sprint_length_days": sprint["length_days"] if sprint else self.settings.integer(EstimatesOptions.SPRINT_LENGTH_DAYS)}
        uncertainties = self.scope_uncertainties(quality)
        uncertainties.extend(row["task_id"] for row in scope if row.get("approved_scope") is False)
        if sprint is None and capacity_days:
            uncertainties.extend(row["task_id"] for row in scope if isinstance(row.get("task_id"), int))
        return {"as_of": now.isoformat(), "calendar": calendar, "scope": scope,
                "scope_uncertainties": uncertainties, "accepted_deliveries": self.accepted_deliveries(histories),
                "capacity_days": capacity_days, "execution_merges": self.execution_merges(reports),
                "trials": self.settings.integer(EstimatesOptions.FORECAST_TRIALS),
                "horizon_sprints": self.settings.integer(EstimatesOptions.FORECAST_HORIZON_SPRINTS)}

    def plan_histories(self, actor: Actor, extra_plan_id: int = 0) -> list[dict]:
        return self.plan_histories_for(self.sprints.index(actor), actor, extra_plan_id)

    def plan_histories_for(self, sprints: list[dict], actor: Actor, extra_plan_id: int = 0) -> list[dict]:
        plan_ids = {plan_id for sprint in sprints for plan_id in sprint["plan_ids"]}
        if extra_plan_id:
            plan_ids.add(extra_plan_id)
        return [self.history.read(plan_id, actor) for plan_id in sorted(plan_ids)]

    def sprint_scope(self, report: dict, histories: list[dict]) -> list[dict]:
        task_histories = {row["task_id"]: {**row, "plan_id": history["scope"]["plan_id"]}
                          for history in histories for row in history["tasks"]}
        approved_plans = {row["scope"]["plan_id"]: self.approved(row["scope"]["plan_state"]) for row in histories}
        lines = [*report["scope"]["baseline"]["lines"], *report["scope"]["added"]["lines"]]
        removed = {row["task_id"] for row in report["scope"]["removed"]["lines"]}
        scope = [self.scope_task(line, task_histories.get(line["task_id"], {}), approved_plans.get(line["plan_id"], False)) for line in lines
                 if line["task_id"] not in removed]
        if report["sprint"]["state"] == "draft":
            for row in scope:
                row["approved_scope"] = False
        return scope

    def scope_task(self, line: dict, history: dict, approved_scope: bool) -> dict:
        task = self.history_task(line["plan_id"], history, line)
        delivery = history.get("delivery", {})
        task["delivery_status"] = delivery.get("status", "unknown")
        task["approved_scope"] = approved_scope
        return task

    @classmethod
    def history_task(cls, plan_id: int, history: dict, frozen: dict | None = None) -> dict:
        estimate = history.get("estimate_history", {})
        sizes = estimate.get("history", ())
        latest = sizes[-1] if sizes else {}
        current_size = estimate.get("current_size")
        frozen_size = frozen.get("size_points") if frozen else None
        if isinstance(current_size, int) and not isinstance(current_size, bool):
            size_points = current_size
        elif sizes:
            size_points = None
        else:
            size_points = frozen_size
        if sizes:
            size_version = latest.get("scale_version")
        elif frozen is not None:
            size_version = frozen.get("size_scale_version")
        else:
            size_version = estimate.get("current_scale_version")
        delivery = history.get("delivery", {})
        domain = frozen.get("domain") if frozen is not None else delivery.get("domain")
        criteria_version = frozen.get("criteria_version") if frozen is not None else delivery.get("criteria_version")
        cohort = {"domain": domain,
                  "size_scale_version": size_version,
                  "criteria_version": criteria_version,
                  **cls.model_tier(history.get("outcomes", ()))}
        return {"plan_id": plan_id, "task_id": history.get("task_id"), "size_points": size_points,
                "cohort": cohort, "delivery_status": delivery.get("status", "unknown")}

    @staticmethod
    def model_tier(outcomes: list[dict]) -> dict:
        for row in reversed(outcomes):
            dimensions = row.get("cohort_dimensions") or {}
            if dimensions.get("model") and dimensions.get("tier"):
                return {"model": dimensions["model"], "tier": dimensions["tier"]}
        return {"model": None, "tier": None}

    @classmethod
    def accepted_deliveries(cls, histories: list[dict]) -> list[dict]:
        output = []
        seen = set()
        for history in histories:
            for task in history["tasks"]:
                evidence_id = task.get("delivery", {}).get("evidence_id")
                for outcome in task.get("outcomes", ()):
                    details = outcome.get("details", {})
                    if (evidence_id is None or outcome.get("kind") not in ("delivery_accepted", "delivery_corrected")
                            or details.get("delivery_id") != evidence_id or not outcome.get("occurred_at")):
                        continue
                    identity = (task["task_id"], evidence_id)
                    if identity in seen:
                        continue
                    seen.add(identity)
                    cohort = outcome.get("cohort_dimensions") or {}
                    model_tier = cls.model_tier_before(task.get("outcomes", ()), outcome.get("occurred_at"))
                    points = cls.outcome_size(outcome)
                    output.append({"task_id": task["task_id"], "size_points": points,
                                   "cohort": BaselineForecast.cohort({**cohort, **model_tier}),
                                   "kind": outcome["kind"], "generation": details.get("generation", 1), "current": True})
        return output

    @classmethod
    def model_tier_before(cls, outcomes: list[dict], occurred_at: str | None) -> dict:
        eligible = [row for row in outcomes if not occurred_at or (row.get("occurred_at") or "") <= occurred_at]
        return cls.model_tier(eligible)

    @staticmethod
    def outcome_size(outcome: dict) -> int | None:
        return outcome.get("committed_size") if outcome.get("committed_size") is not None else outcome.get("planned_size")

    @classmethod
    def delivery_batches(cls, histories: list[dict], timezone_name: str) -> dict[str, dict[str, dict[str, int]]]:
        batches: dict[str, dict[str, dict[str, int]]] = {}
        seen = set()
        zone = ZoneInfo(timezone_name)
        for history in histories:
            for task in history["tasks"]:
                evidence_id = task.get("delivery", {}).get("evidence_id")
                for outcome in task.get("outcomes", ()):
                    details = outcome.get("details", {})
                    if (evidence_id is None or outcome.get("kind") not in ("delivery_accepted", "delivery_corrected")
                            or details.get("delivery_id") != evidence_id):
                        continue
                    identity = (task["task_id"], evidence_id)
                    if identity in seen:
                        continue
                    seen.add(identity)
                    stamp = outcome.get("occurred_at")
                    if not stamp:
                        continue
                    moment = datetime.fromisoformat(stamp.replace("Z", "+00:00"))
                    day = moment.astimezone(zone).date().isoformat()
                    dimensions = outcome.get("cohort_dimensions") or {}
                    cohort = BaselineForecast.cohort({**dimensions, **cls.model_tier_before(task.get("outcomes", ()), stamp)})
                    key = BaselineForecast.cohort_key(cohort)
                    points = cls.outcome_size(outcome)
                    if not isinstance(points, int) or isinstance(points, bool) or points <= 0:
                        continue
                    batch = batches.setdefault(day, {}).setdefault(str(details.get("delivery_id")), {})
                    batch[key] = batch.get(key, 0) + points
        return batches

    @staticmethod
    def capacity_days(reports: list[dict], batches: dict) -> list[dict]:
        days = {}
        for report in reports:
            for row in report["days"]:
                actual = row["availability"].get("actual_places")
                if not isinstance(actual, int) or isinstance(actual, bool):
                    continue
                date = row["date"]
                deployment_batches = [{"batch_id": key, "points_by_cohort": points}
                                      for key, points in sorted(batches.get(date, {}).items())]
                days[date] = {"date": date, "available_places": actual, "deployment_batches": deployment_batches}
        return [days[key] for key in sorted(days)]

    @staticmethod
    def plan_result(forecast: dict, plan_id: int, source: dict) -> dict:
        plan = next((row for row in forecast.get("plan_forecasts", ()) if row["plan_id"] == plan_id), None)
        scope_rows = [row for row in source["scope"] if row["plan_id"] == plan_id]
        scope, unknown_sizes, unknown_domains, unknown_cohorts = BaselineForecast.scope(scope_rows)
        task_ids = {row["task_id"] for row in scope_rows}
        unknown_scope = {row for row in source["scope_uncertainties"] if row in task_ids}
        if plan is None:
            return {**forecast, "plan_id": plan_id, "scope": BaselineForecast.scope_summary(scope, scope_rows),
                    "unknown_sizes": unknown_sizes, "unknown_domains": unknown_domains,
                    "unknown_constraints": sorted(set(unknown_cohorts) | unknown_scope), "plan_forecasts": []}
        return {**forecast, **plan, "scope": BaselineForecast.scope_summary(scope, scope_rows),
                "shared_sprint_scope": forecast.get("scope"), "plan_id": plan_id,
                "unknown_sizes": unknown_sizes, "unknown_domains": unknown_domains,
                "unknown_constraints": sorted(set(unknown_cohorts) | unknown_scope), "plan_forecasts": [plan]}

    def sprint_forecast(self, forecast: dict, source: dict, sprint: dict, histories: list[dict]) -> dict:
        history_by_plan = {row["scope"]["plan_id"]: row for row in histories}
        distributions = {row["plan_id"]: row for row in forecast.get("plan_forecasts", ())}
        freshness = self.capacity_freshness(forecast, source)
        rows = []
        for plan_id in sprint["plan_ids"]:
            history = history_by_plan[plan_id]
            scope_rows = [row for row in source["scope"] if row["plan_id"] == plan_id]
            scope, _unknown_sizes, _unknown_domains, _unknown_cohorts = BaselineForecast.scope(scope_rows)
            rows.append({**{key: value for key, value in forecast.items() if key != "plan_forecasts"}, **freshness,
                         **distributions.get(plan_id, {}), "plan_id": plan_id,
                         "scope": BaselineForecast.scope_summary(scope, scope_rows),
                         **self.delivery_summary(history)})
        return {**forecast, **freshness, "sprint": sprint, "plan_forecasts": rows}

    def delivery_summary(self, history: dict) -> dict:
        delivery_tasks = history["delivery"]["tasks"]
        task_histories = {row["task_id"]: row for row in history["tasks"] if row["current_in_plan"]}
        delivered = sorted(row["task_id"] for row in delivery_tasks if row["status"] == "delivered")
        awaiting = [row for row in delivery_tasks if row["status"] == "awaiting_deployment"]
        current = list(task_histories.values())
        sizes = {row["task_id"]: row["estimate_history"]["current_size"] for row in current}
        remaining_sizes = [sizes[row["task_id"]] for row in delivery_tasks
                           if row["task_id"] not in delivered]
        criteria = self.domain_criteria(delivery_tasks)
        status = self.delivery_status(history["delivery"]["status"], delivery_tasks)
        oldest, age = self.awaiting_age(awaiting, task_histories)
        unknown_sizes = sum(value is None for value in remaining_sizes)
        return {"delivery_status": status,
                "delivery_complete": bool(delivery_tasks) and len(delivered) == len(delivery_tasks),
                "execution_complete": bool(current) and all(row["execution"].get("artifact_accepted") is True for row in current),
                "latest_delivery_at": self.latest_delivery_at(history),
                "delivered_scope": delivered,
                "current_scope": {"task_ids": sorted(sizes), "task_count": len(current),
                                  "delivered_count": len(delivered), "remaining_count": len(remaining_sizes),
                                  "remaining_points": None if unknown_sizes else sum(remaining_sizes),
                                  "unknown_size_tasks": unknown_sizes},
                "awaiting_deploy_count": len(awaiting),
                "awaiting_deploy_oldest_since": oldest,
                "awaiting_deploy_oldest_age_days": round(age / 86400, 1) if age is not None else None,
                "domain_criteria": criteria,
                "missing_criteria": sorted({row["reason"] for row in delivery_tasks if row["status"] == "unknown" and row["reason"]})}

    @staticmethod
    def latest_delivery_at(history: dict) -> str | None:
        accepted = []
        for task in history["tasks"]:
            evidence_id = task.get("delivery", {}).get("evidence_id")
            accepted.extend(outcome["occurred_at"] for outcome in task.get("outcomes", ())
                            if evidence_id is not None and outcome.get("kind") in ("delivery_accepted", "delivery_corrected")
                            and outcome.get("details", {}).get("delivery_id") == evidence_id and outcome.get("occurred_at"))
        return max(accepted, default=None)

    @staticmethod
    def domain_criteria(tasks: list[dict]) -> list[dict]:
        criteria = {}
        for task in tasks:
            definition = task.get("definition_of_done")
            if not definition:
                continue
            key = (task.get("domain"), task.get("criteria_version"))
            criteria[key] = {"domain": key[0], "version": key[1],
                             "criterion": definition.get("criterion", ""),
                             "evidence": definition.get("evidence", ""),
                             "target": definition.get("target", "")}
        return [criteria[key] for key in sorted(criteria, key=lambda row: (row[0] or "", row[1] or ""))]

    @staticmethod
    def delivery_status(status: str, tasks: list[dict]) -> str:
        if status == "unknown":
            return next((row["reason"] for row in tasks if row["reason"]), "definition of done not set")
        return {"awaiting_deployment": "awaiting deployment", "awaiting_evidence": "awaiting evidence",
                "awaiting_merge": "awaiting merge", "awaiting_execution": "awaiting execution"}.get(status, status)

    def awaiting_age(self, awaiting: list[dict], histories: dict[int, dict]) -> tuple[str | None, int | None]:
        if not awaiting:
            return None, None
        stamps = [self.delivery_wait_since(histories.get(row["task_id"], {})) for row in awaiting]
        if any(stamp is None for stamp in stamps):
            return None, None
        oldest = min(stamps)
        since = datetime.fromisoformat(oldest.replace("Z", "+00:00"))
        age = int((self.time_source.moment().astimezone(timezone.utc) - since.astimezone(timezone.utc)).total_seconds())
        return oldest, max(0, age)

    @staticmethod
    def delivery_wait_since(history: dict) -> str | None:
        kinds = {"task_completed", "worker_work_merged", "delivery_reopened"}
        events = [row for row in history.get("outcomes", ()) if row.get("kind") in kinds and row.get("occurred_at")]
        latest = max(events, key=lambda row: row["occurred_at"], default=None)
        return latest["occurred_at"] if latest else None

    @staticmethod
    def capacity_freshness(forecast: dict, source: dict) -> dict:
        as_of = forecast.get("as_of")
        observed = [row["date"] for row in source["capacity_days"]
                    if as_of and row["date"] <= as_of and isinstance(row["available_places"], int)
                    and not isinstance(row["available_places"], bool)]
        latest = max(observed, default=None)
        age = (datetime.fromisoformat(as_of).date() - datetime.fromisoformat(latest).date()).days if as_of and latest else None
        sprint_days = source["calendar"]["sprint_length_days"]
        freshness = "unknown" if age is None else "stale" if age > sprint_days else "fresh"
        return {"capacity_observed_through": latest, "capacity_age_days": age, "capacity_freshness": freshness}

    def plan_sprint(self, plan: Plan) -> Sprint | None:
        periods = [self.sprints.find(ref.id) for ref in self.sprints.links.sources(plan, SPRINT_PLAN)]
        periods.sort(key=lambda row: (row.starts_at, row.row_id), reverse=True)
        return next((row for row in periods if row.state != SprintState.CLOSED), periods[0] if periods else None)

    @staticmethod
    def scope_uncertainties(quality: dict) -> list[int]:
        names = {"scope_removal", "scope_addition_time"}
        return sorted({row["task_id"] for row in quality.get("flags", ()) if row.get("name") in names and "task_id" in row})

    @staticmethod
    def approved(plan_state: str | None) -> bool:
        return plan_state in ("approved", "started", "paused", "delegated", "blocked", "done")

    @staticmethod
    def execution_merges(reports: list[dict]) -> int:
        return sum(row.get("task_count", 0) for report in reports for row in report["throughput"]["execution"])

    @staticmethod
    def timezone(reports: list[dict]) -> str:
        latest = max(reports, key=lambda row: row["sprint"]["starts_at"], default=None)
        return latest["sprint"]["timezone"] if latest else "Europe/Amsterdam"

    @staticmethod
    def next_end(sprint: dict, reports: list[dict]) -> str | None:
        later = [row["sprint"] for row in reports if row["sprint"]["starts_at"] >= sprint["ends_at"]]
        return min(later, key=lambda row: row["starts_at"])["ends_on"] if later else None
