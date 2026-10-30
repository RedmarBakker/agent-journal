from datetime import date, datetime, time, timedelta, timezone
from zoneinfo import ZoneInfo

from journal.models.support.ref import Ref
from journal.repositories.forecast_snapshots import ForecastSnapshots
from journal.repositories.plan_outcome_history import PlanOutcomeHistory
from journal.repositories.plans import PLAN_LINK
from journal.repositories.sprints import Sprints
from journal.support.actor import Actor
from journal.support.rejection import Rejection


SPRINT_METRICS_VERSION = "sprint-metrics-v1"
EXECUTION_EVENTS = ("task_completed", "worker_work_merged")
DELIVERY_EVENTS = ("delivery_accepted", "delivery_corrected")


class SprintOutcomeMetrics:
    """The owner-scoped sprint execution, delivery, velocity and scope projection."""

    def __init__(self, sprints: Sprints, history: PlanOutcomeHistory, snapshots: ForecastSnapshots) -> None:
        self.sprints, self.history, self.snapshots = sprints, history, snapshots

    def read(self, sprint_id: int, actor: Actor) -> dict:
        sprint, histories = self.source(sprint_id, actor)
        report = self.project(sprint, histories)
        retrospective = next((row["data"] for row in sprint["changes"] if row["change_type"] == "sprint_closed"), None)
        return {**report, **({"retrospective": retrospective} if retrospective else {})}

    def close_report(self, sprint_id: int, actor: Actor) -> dict:
        sprint, histories = self.source(sprint_id, actor)
        projection = self.project(sprint, histories)
        plan_ids = {row["plan_id"] for row in sprint["commitments"]} | set(sprint["plan_ids"])
        plan_ids.update(row["plan_id"] for row in sprint["changes"] if row.get("plan_id"))
        snapshots = self.saved_forecasts(sprint_id, sorted(plan_ids))
        scope_lines = [*projection["scope"]["baseline"]["lines"], *projection["scope"]["added"]["lines"]]
        task_histories = {(history["scope"]["plan_id"], task["task_id"]): task
                          for history in histories for task in history["tasks"]}
        removed_ids = set(projection["scope"]["removed"]["task_ids"])
        delivered_ids = []
        remaining_ids = []
        scope_task_ids = {(line["plan_id"], line["task_id"]) for line in scope_lines}
        removed_ids.update(task_id for (plan_id, task_id), task in task_histories.items()
                           if (plan_id, task_id) in scope_task_ids
                           and (not task["current_in_plan"] or task["execution"]["current_task_state"] == "cancelled"))
        for line in scope_lines:
            task = task_histories.get((line["plan_id"], line["task_id"]))
            if line["task_id"] in removed_ids:
                continue
            if task and task["delivery"]["status"] == "delivered":
                delivered_ids.append(line["task_id"])
            else:
                remaining_ids.append(line["task_id"])
        delivered_ids.sort()
        remaining_ids.sort()
        sprint_row = self.sprints.find(sprint_id)
        task_outcomes = [self.task_close_outcome(sprint_row, line, task_histories.get((line["plan_id"], line["task_id"])),
                                                "delivered" if line["task_id"] in delivered_ids else
                                                "removed" if line["task_id"] in removed_ids else "remaining")
                         for line in scope_lines]
        cost_rows = [row["measurements"]["cost"] for row in task_outcomes]
        measured_costs = [row for row in task_outcomes if row["measurements"]["cost"]["status"] == "measured"]
        cost_availability = {"status": self.cost_status(len(measured_costs), len(cost_rows)),
                             "measured_task_ids": [row["task_id"] for row in measured_costs],
                             "unmeasured_task_ids": [row["task_id"] for row in task_outcomes if row["measurements"]["cost"]["status"] != "measured"]}
        return {"schema_version": "sprint-retrospective-v1",
                "planned": {key: sprint[key] for key in ("starts_on", "ends_on", "starts_at", "ends_at", "timezone", "length_days", "calendar_version")}
                           | {"commitments": sprint["commitments"]},
                "actual": {"started_at": sprint["started_at"]},
                "forecasts": {"status": "recorded" if snapshots else "not_enough_history", "snapshots": snapshots},
                "scope_at_close": {"originally_committed_task_ids": projection["scope"]["baseline"]["task_ids"],
                                   "added_task_ids": projection["scope"]["added"]["task_ids"],
                                   "scope_task_ids": sorted({line["task_id"] for line in scope_lines}),
                                   "delivered_task_ids": delivered_ids, "remaining_task_ids": remaining_ids,
                                   "removed_task_ids": sorted(removed_ids),
                                   "delivered_by_domain": self.domain_scope(scope_lines, set(delivered_ids)),
                                   "remaining_by_domain": self.domain_scope(scope_lines, set(remaining_ids))},
                "task_outcomes": task_outcomes, "cost_availability": cost_availability,
                "range_errors": self.range_errors(snapshots, task_outcomes)}

    def remaining_task_ids(self, sprint_id: int, plan_id: int, actor: Actor) -> list[int]:
        sprint = self.sprints.show(sprint_id, actor)
        closure = next((row["data"] for row in sprint["changes"] if row["change_type"] == "sprint_closed"), None)
        if closure is None:
            raise Rejection("carry-over needs a closed sprint retrospective")
        committed = {row["task_id"] for row in closure["task_outcomes"]
                     if row["plan_id"] == plan_id and row["scope_status"] == "remaining"}
        history = self.history.read(plan_id, actor)
        return sorted(task["task_id"] for task in history["tasks"] if task["task_id"] in committed
                      and task["current_in_plan"] and task["delivery"]["status"] != "delivered"
                      and task["execution"]["current_task_state"] != "cancelled")

    def source(self, sprint_id: int, actor: Actor) -> tuple[dict, list[dict]]:
        sprint = self.sprints.show(sprint_id, actor)
        plan_ids = {row["plan_id"] for row in sprint["commitments"]}
        plan_ids.update(sprint["plan_ids"])
        plan_ids.update(row["plan_id"] for row in sprint["changes"] if row.get("plan_id"))
        histories = [self.history.read(plan_id, actor) for plan_id in sorted(plan_ids)]
        self.enrich_plan_links(histories)
        self.enrich_audit(sprint, histories, sprint_id)
        return sprint, histories

    def saved_forecasts(self, sprint_id: int, plan_ids: list[int]) -> list[dict]:
        scopes = [("sprint", self.sprints.find(sprint_id)),
                  *(("plan", self.sprints.plans.find(plan_id)) for plan_id in plan_ids)]
        rows = [(row.captured_at, row.row_id,
                 {"id": row.row_id, "scope": {"kind": kind, "id": scope.row_id}, "input_cut": row.input_cut,
                  "captured_at": self.timestamp(datetime.fromtimestamp(row.captured_at, timezone.utc)),
                  "method_version": row.method_version, "data": row.data})
                for kind, scope in scopes for row in self.snapshots.for_scope(scope)]
        return [snapshot for _captured, _id, snapshot in sorted(rows)]

    def task_close_outcome(self, sprint, line: dict, task: dict | None, status: str) -> dict:
        plan = self.sprints.plans.find(line["plan_id"])
        scope_snapshot = self.sprints.task_snapshot_in_sprint(sprint, plan, line["task_id"])
        if scope_snapshot is None:
            task_row = self.sprints.tasks.find(line["task_id"])
            scope_snapshot = self.sprints.task_snapshot(task_row, self.sprints.size_scale.version())
        if task is None:
            return {"task_id": line["task_id"], "plan_id": line["plan_id"], "domain": line["domain"],
                    "size_points": line["size_points"], "scope_status": status, "scope_snapshot": scope_snapshot,
                    "measurements": {"cost": {"status": "not_measured", "label": "Not measured"}}}
        return {"task_id": line["task_id"], "plan_id": line["plan_id"], "domain": line["domain"],
                "size_points": line["size_points"], "scope_status": status, "current_task_state": task["execution"]["current_task_state"],
                "scope_snapshot": scope_snapshot, "measurements": task["measurements"],
                "execution": task["execution"], "outcomes": task["outcomes"],
                "delivery": task["delivery"]}

    @staticmethod
    def domain_scope(lines: list[dict], included: set[int]) -> list[dict]:
        groups = {}
        for line in lines:
            if line["task_id"] not in included:
                continue
            group = groups.setdefault(line["domain"], {"domain": line["domain"], "task_ids": [], "known_size_points": 0,
                                                          "unknown_size_tasks": 0})
            group["task_ids"].append(line["task_id"])
            if line["size_points"] is None:
                group["unknown_size_tasks"] += 1
            else:
                group["known_size_points"] += line["size_points"]
        return [{**groups[key], "task_ids": sorted(groups[key]["task_ids"]), "task_count": len(groups[key]["task_ids"])}
                for key in sorted(groups, key=lambda domain: domain or "")]

    @staticmethod
    def cost_status(measured: int, total: int) -> str:
        if not measured:
            return "not_measured"
        return "measured" if measured == total else "partially_measured"

    @classmethod
    def range_errors(cls, snapshots: list[dict], outcomes: list[dict]) -> dict:
        errors = []
        censored = []
        by_plan = {}
        for row in outcomes:
            by_plan.setdefault(row["plan_id"], []).append(row)
        for snapshot in snapshots:
            forecast = snapshot["data"].get("forecast", {})
            for plan_forecast in forecast.get("plan_forecasts", ()) if forecast.get("status") == "forecast" else ():
                plan_id = plan_forecast.get("plan_id")
                tasks = by_plan.get(plan_id, [])
                if not tasks or any(row["scope_status"] != "delivered" for row in tasks):
                    censored.append(plan_id)
                    continue
                delivered_at = [row.get("measurements", {}).get("delivery", {}).get("accepted_at") for row in tasks]
                if any(not stamp for stamp in delivered_at):
                    censored.append(plan_id)
                    continue
                actual = max(delivered_at)
                errors.append({"plan_id": plan_id, "forecast_snapshot_id": snapshot["id"], "actual_delivery_at": actual,
                               "p50": plan_forecast.get("p50"), "p85": plan_forecast.get("p85"),
                               "p50_error_days": cls.day_error(actual, plan_forecast.get("p50")),
                               "p85_error_days": cls.day_error(actual, plan_forecast.get("p85"))})
        status = "measured" if errors else "censored" if censored else "not_enough_history"
        return {"status": status, "forecasts": errors, "censored_plan_ids": sorted(set(censored))}

    @classmethod
    def day_error(cls, actual: str, predicted: str | None) -> int | None:
        if not predicted:
            return None
        actual_moment = cls.moment(actual)
        try:
            predicted_day = date.fromisoformat(predicted[:10])
        except ValueError:
            return None
        return (actual_moment.date() - predicted_day).days if actual_moment else None

    def enrich_plan_links(self, histories: list[dict]) -> None:
        for history in histories:
            plan = self.sprints.plans.find(history["scope"]["plan_id"])
            current_tasks = {task.row_id: task for task in self.sprints.plans.plan_tasks(plan)}
            for task in history["tasks"]:
                row = current_tasks.get(task["task_id"])
                if row is None:
                    continue
                link = next((link for link in self.sprints.links.source_links(row, PLAN_LINK) if link.target == Ref.build(plan)), None)
                if link:
                    task["plan_link_recorded_at"] = self.timestamp(link.created_at)
                    task["plan_link_actor"] = link.creator.stamp if link.creator else ""

    def enrich_audit(self, sprint: dict, histories: list[dict], sprint_id: int) -> None:
        commitments = {}
        changes = {}
        for history in histories:
            for period in history["sprints"]:
                if period["id"] != sprint_id:
                    continue
                commitments.update({row["id"]: row for row in period["commitments"]})
                changes.update({row["id"]: row for row in period["changes"]})
        for commitment in sprint["commitments"]:
            audit = commitments.get(commitment["id"], {})
            commitment.update({key: audit[key] for key in ("actor", "recorded_at") if key in audit})
        for change in sprint["changes"]:
            audit = changes.get(change["id"], {})
            change.update({key: audit[key] for key in ("actor", "recorded_at") if key in audit})

    @classmethod
    def project(cls, sprint: dict, histories: list[dict]) -> dict:
        task_histories = {task["task_id"]: {**task, "plan_id": history["scope"]["plan_id"]}
                          for history in histories for task in history["tasks"]}
        baseline, added, removed, flags = cls.scope_lines(sprint, task_histories)
        lines = {line["task_id"]: line for line in (*baseline, *added)}
        task_facts = {task_id: cls.facts(task_histories.get(task_id, {})) for task_id in lines}
        start, end = cls.moment(sprint["starts_at"]), cls.moment(sprint["ends_at"])
        zone = ZoneInfo(sprint["timezone"])
        days = cls.daily(sprint, lines, task_facts, start, end, zone)
        throughput = cls.throughput(lines, task_facts, start, end)
        ranges = cls.ranges(lines, task_facts, start, end)
        velocity = {"status": "closed", "by_cohort": throughput["delivered"]} if sprint["state"] == "closed" else {"status": "in_progress", "by_cohort": None}
        unknown_size = sorted(task_id for task_id, line in lines.items() if line["size_points"] is None)
        if unknown_size:
            flags.append({"name": "unknown_size", "task_ids": unknown_size, "reason": "Unknown-size work remains separate from sized work."})
        missing_event_time = sorted(task_id for task_id, facts in task_facts.items() if any(not row.get("recorded_at") for row in facts))
        if missing_event_time:
            flags.append({"name": "event_timestamp", "task_ids": missing_event_time, "status": "incomplete"})
        flags.append({"name": "availability", "status": "not_measured", "reason": "No daily availability or actual-place observations are recorded."})
        return {"schema_version": SPRINT_METRICS_VERSION,
                "sprint": {key: sprint[key] for key in ("id", "starts_on", "ends_on", "starts_at", "ends_at", "timezone", "length_days", "state")},
                "scope": {"baseline": cls.scope_summary(baseline), "added": cls.scope_summary(added), "removed": cls.scope_summary(removed)},
                "throughput": throughput,
                "velocity": velocity,
                "ranges_by_size": ranges,
                "availability": {"status": "not_measured", "daily_observations": None},
                "days": days,
                "comparability": {"group_by": ["domain", "size_scale_version", "criteria_version", "model", "tier"],
                                  "note": "Compare only matching cohorts; domains and size-scale versions use different units."},
                "data_quality": {"status": "incomplete", "flags": flags}}

    @classmethod
    def scope_lines(cls, sprint: dict, task_histories: dict[int, dict]) -> tuple[list[dict], list[dict], list[dict], list[dict]]:
        baseline = {}
        added = {}
        flags = []
        for commitment in sprint["commitments"]:
            for task in commitment.get("tasks", ()):
                line = cls.scope_line(task, commitment["plan_id"], "baseline", commitment.get("actor"), commitment.get("recorded_at"), "")
                baseline.setdefault(line["task_id"], line)
        for change in sprint["changes"]:
            if change["change_type"] != "plan_added":
                continue
            for task in change.get("data", {}).get("tasks", ()):
                line = cls.scope_line(task, change["plan_id"], "plan_added", change.get("actor"), change.get("recorded_at") or change.get("created_at"), change.get("reason", ""))
                if line["task_id"] not in baseline:
                    added.setdefault(line["task_id"], line)
        for history in task_histories.values():
            if not history.get("current_in_plan"):
                continue
            task_id = history["task_id"]
            if task_id in baseline or task_id in added:
                continue
            line = cls.late_scope_line(history)
            if line:
                start = cls.moment(sprint["starts_at"])
                end = cls.moment(sprint["ends_at"])
                moment = cls.moment(line.get("recorded_at"))
                if moment is None or cls.in_period(moment, start, end):
                    added[task_id] = line
                if not line["recorded_at"]:
                    flags.append({"name": "scope_addition_time", "task_id": task_id, "status": "incomplete"})
        lines = {**baseline, **added}
        removed = {}
        for task_id, history in task_histories.items():
            line = lines.get(task_id)
            if line is None:
                continue
            cancelled = next((row for row in cls.facts(history) if row["kind"] == "task_cancelled"), None)
            when = cls.moment(cancelled.get("recorded_at")) if cancelled else None
            if cancelled and when and cls.in_period(when, cls.moment(sprint["starts_at"]), cls.moment(sprint["ends_at"])):
                removed[task_id] = {**line, "change_type": "task_cancelled", "actor": cancelled.get("actor", ""),
                                    "recorded_at": cancelled.get("recorded_at"), "reason": cancelled.get("details", {}).get("reason", "")}
            elif task_id in baseline and history.get("current_in_plan") is False:
                flags.append({"name": "scope_removal", "task_id": task_id, "status": "not_recorded",
                              "reason": "The task left the current plan without a recorded sprint scope change."})
        return sorted(baseline.values(), key=cls.line_order), sorted(added.values(), key=cls.line_order), sorted(removed.values(), key=cls.line_order), flags

    @classmethod
    def scope_line(cls, task: dict, plan_id: int, change_type: str, actor: str | None, recorded_at: str | None, reason: str) -> dict:
        return {"task_id": task["id"], "plan_id": plan_id, "title": task.get("title", ""), "domain": task.get("domain"),
                "size_points": cls.size(task.get("size")), "size_scale_version": task.get("size_scale_version"),
                "criteria_version": task.get("criteria_version"),
                "delivery_evidence": (task.get("definition_of_done") or {}).get("evidence"), "change_type": change_type,
                "actor": actor or "", "recorded_at": recorded_at, "reason": reason}

    @classmethod
    def late_scope_line(cls, history: dict) -> dict | None:
        estimates = history.get("estimate_history", {}).get("history", ())
        first = next((row for row in estimates if row["change_type"] == "planning_baseline"), None)
        if first:
            size, scale_version = first.get("size"), first.get("scale_version")
        else:
            size, scale_version = None, None
        return {"task_id": history["task_id"], "plan_id": history.get("plan_id", 0),
                "title": history.get("title", ""), "domain": history.get("delivery", {}).get("domain"), "size_points": cls.size(size),
                "size_scale_version": scale_version, "criteria_version": history.get("delivery", {}).get("criteria_version"),
                "delivery_evidence": (history.get("delivery", {}).get("definition_of_done") or {}).get("evidence"),
                "change_type": "task_added", "actor": history.get("plan_link_actor", ""),
                "recorded_at": history.get("plan_link_recorded_at"), "reason": ""}

    @classmethod
    def scope_summary(cls, lines: list[dict]) -> dict:
        return {"task_ids": [row["task_id"] for row in lines], "task_count": len(lines),
                "known_size_points": sum(row["size_points"] or 0 for row in lines),
                "unknown_size_tasks": sum(row["size_points"] is None for row in lines), "lines": lines}

    @classmethod
    def daily(cls, sprint: dict, lines: dict[int, dict], task_facts: dict[int, list[dict]], start: datetime, end: datetime,
              zone: ZoneInfo) -> list[dict]:
        rows = []
        first_day = date.fromisoformat(sprint["starts_on"])
        for offset in range(sprint["length_days"]):
            day = first_day + timedelta(days=offset)
            after = datetime.combine(day + timedelta(days=1), time.min, zone).astimezone(timezone.utc)
            as_of = after - timedelta(microseconds=1)
            active = {task_id: line for task_id, line in lines.items() if cls.available_by(line, after, start)}
            states = {task_id: cls.flow_state(active[task_id], task_facts[task_id], as_of) for task_id in active}
            remaining = [line for task_id, line in active.items() if states[task_id] not in ("delivered", "removed")]
            daily_execution = cls.daily_output(active, task_facts, day, EXECUTION_EVENTS, start, end, zone)
            daily_delivery = cls.daily_output(active, task_facts, day, DELIVERY_EVENTS, start, end, zone)
            rows.append({"date": day.isoformat(), "availability": {"status": "not_measured", "available_places": None, "actual_places": None},
                         "zero_output": None, "scope_added_tasks": sum(cls.event_day(line.get("recorded_at"), zone) == day for line in active.values() if line["change_type"] in ("plan_added", "task_added")),
                         "scope_removed_tasks": sum(cls.event_day(next((row.get("recorded_at") for row in task_facts[task_id] if row["kind"] == "task_cancelled"), None), zone) == day for task_id in active),
                         "execution": daily_execution, "delivered": daily_delivery,
                         "remaining": cls.aggregate_scope(remaining), "cumulative_flow": cls.flow(active, states)})
        return rows

    @classmethod
    def throughput(cls, lines: dict[int, dict], task_facts: dict[int, list[dict]], start: datetime, end: datetime) -> dict:
        execution = []
        delivered = []
        for task_id, line in lines.items():
            facts = task_facts[task_id]
            execution_row = cls.first_in_period(facts, EXECUTION_EVENTS, start, end)
            delivery_row = cls.first_in_period(facts, DELIVERY_EVENTS, start, end)
            if execution_row:
                execution.append((line, execution_row))
            if delivery_row:
                delivered.append((line, delivery_row))
        return {"execution": cls.aggregate_events(execution), "delivered": cls.aggregate_events(delivered),
                "by_cohort": cls.merge_throughput(execution, delivered)}

    @classmethod
    def merge_throughput(cls, execution: list[tuple[dict, dict]], delivered: list[tuple[dict, dict]]) -> list[dict]:
        result = {}
        for label, values in (("execution", execution), ("delivered", delivered)):
            for line, event in values:
                key = cls.event_key(line, event)
                row = result.setdefault(key, {**cls.event_cohort(line, event), "execution": cls.empty_count(), "delivered": cls.empty_count()})[label]
                cls.credit(row, line)
        return [result[key] for key in sorted(result)]

    @classmethod
    def aggregate_events(cls, values: list[tuple[dict, dict]]) -> list[dict]:
        groups = {}
        for line, event in values:
            key = cls.event_key(line, event)
            row = groups.setdefault(key, {**cls.event_cohort(line, event), **cls.empty_count()})
            cls.credit(row, line)
        return [groups[key] for key in sorted(groups)]

    @classmethod
    def daily_output(cls, lines: dict[int, dict], facts: dict[int, list[dict]], day: date, kinds: tuple[str, ...], start: datetime,
                     end: datetime, zone: ZoneInfo) -> list[dict]:
        groups = {cls.scope_key(line): {**cls.scope_cohort(line), **cls.empty_count()} for line in lines.values()}
        for task_id, line in lines.items():
            event = cls.first_on_day(facts[task_id], kinds, day, start, end, zone)
            if event:
                cls.credit(groups[cls.scope_key(line)], line)
        return [groups[key] for key in sorted(groups)]

    @classmethod
    def aggregate_scope(cls, lines: list[dict]) -> list[dict]:
        groups = {}
        for line in lines:
            key = cls.scope_key(line)
            row = groups.setdefault(key, {**cls.scope_cohort(line), **cls.empty_count()})
            cls.credit(row, line)
        return [groups[key] for key in sorted(groups)]

    @classmethod
    def flow(cls, lines: dict[int, dict], states: dict[int, str]) -> list[dict]:
        groups = {}
        for task_id, line in lines.items():
            key = cls.scope_key(line)
            row = groups.setdefault(key, {**cls.scope_cohort(line), "not_started": 0, "executing": 0, "waiting": 0,
                                          "awaiting_deployment": 0, "awaiting_evidence": 0, "delivery_unknown": 0,
                                          "delivered": 0, "removed": 0,
                                          "unknown_size_tasks": 0, "remaining_size_points": 0})
            row[states[task_id]] += 1
            if line["size_points"] is None:
                row["unknown_size_tasks"] += 1
            elif states[task_id] not in ("delivered", "removed"):
                row["remaining_size_points"] += line["size_points"]
        return [groups[key] for key in sorted(groups)]

    @classmethod
    def ranges(cls, lines: dict[int, dict], facts: dict[int, list[dict]], start: datetime, end: datetime) -> list[dict]:
        groups = {}
        for task_id, line in lines.items():
            events = facts[task_id]
            started = next((cls.moment(row.get("recorded_at")) for row in events if row["kind"] == "task_started" and cls.moment(row.get("recorded_at"))), None)
            completion = cls.completion(events, start, end)
            accepted = cls.acceptance_after(events, completion)
            key = (*cls.scope_key(line), line["size_points"])
            row = groups.setdefault(key, {"domain": line["domain"], "size_scale_version": line["size_scale_version"],
                                          "criteria_version": line["criteria_version"], "size_points": line["size_points"],
                                          "cycle_time_seconds": [], "delivery_wait_seconds": [], "right_censored_tasks": 0})
            if started and completion and completion >= started:
                row["cycle_time_seconds"].append((completion - started).total_seconds())
            if completion and accepted:
                row["delivery_wait_seconds"].append((accepted - completion).total_seconds())
            elif completion and not accepted and cls.latest_state(line, events, end) in ("awaiting_deployment", "awaiting_evidence"):
                row["right_censored_tasks"] += 1
        return [cls.range_row(groups[key]) for key in sorted(groups, key=cls.range_order)]

    @staticmethod
    def range_order(key: tuple) -> tuple:
        return (*key[:3], key[3] if key[3] is not None else -1)

    @classmethod
    def range_row(cls, row: dict) -> dict:
        cycle = row["cycle_time_seconds"]
        wait = row["delivery_wait_seconds"]
        return {key: row[key] for key in ("domain", "size_scale_version", "criteria_version", "size_points")} | {
            "cycle_time_seconds": cls.bounds(cycle),
            "delivery_wait_seconds": {**cls.bounds(wait), "right_censored_tasks": row["right_censored_tasks"]}}

    @staticmethod
    def bounds(values: list[float]) -> dict:
        return {"minimum": min(values) if values else None, "maximum": max(values) if values else None, "samples": len(values)}

    @classmethod
    def first_in_period(cls, facts: list[dict], kinds: tuple[str, ...], start: datetime, end: datetime) -> dict | None:
        return next((row for row in facts if row["kind"] in kinds and (moment := cls.moment(row.get("recorded_at"))) and cls.in_period(moment, start, end)), None)

    @classmethod
    def first_on_day(cls, facts: list[dict], kinds: tuple[str, ...], day: date, start: datetime, end: datetime,
                     zone: ZoneInfo) -> dict | None:
        return next((row for row in facts if row["kind"] in kinds and (moment := cls.moment(row.get("recorded_at")))
                     and cls.in_period(moment, start, end) and cls.event_day(row.get("recorded_at"), zone) == day), None)

    @classmethod
    def flow_state(cls, line: dict, facts: list[dict], as_of: datetime) -> str:
        state = "not_started"
        for row in facts:
            moment = cls.moment(row.get("recorded_at"))
            if not moment or moment > as_of:
                continue
            state = cls.flow_change(line, row["kind"], state)
        return state

    @classmethod
    def flow_change(cls, line: dict, kind: str, state: str) -> str:
        if kind in ("task_completed", "worker_work_merged", "delivery_reopened"):
            return cls.pending_delivery(line)
        return {"task_started": "executing", "task_paused": "waiting", "task_blocked": "waiting", "task_testing": "waiting",
                "delivery_accepted": "delivered", "delivery_corrected": "delivered", "task_reopened": "not_started",
                "task_cancelled": "removed"}.get(kind, state)

    @staticmethod
    def pending_delivery(line: dict) -> str:
        evidence = line.get("delivery_evidence")
        if evidence == "production_deployment":
            return "awaiting_deployment"
        return "delivery_unknown" if evidence is None else "awaiting_evidence"

    @classmethod
    def latest_state(cls, line: dict, facts: list[dict], as_of: datetime) -> str:
        return cls.flow_state(line, facts, as_of)

    @classmethod
    def completion(cls, facts: list[dict], start: datetime, end: datetime) -> datetime | None:
        merged = next((cls.moment(row.get("recorded_at")) for row in facts if row["kind"] == "worker_work_merged" and
                       (moment := cls.moment(row.get("recorded_at"))) and cls.in_period(moment, start, end)), None)
        if merged:
            return merged
        return next((cls.moment(row.get("recorded_at")) for row in facts if row["kind"] == "task_completed" and
                     (moment := cls.moment(row.get("recorded_at"))) and cls.in_period(moment, start, end)), None)

    @classmethod
    def acceptance_after(cls, facts: list[dict], completion: datetime | None) -> datetime | None:
        if completion is None:
            return None
        return next((moment for row in facts if row["kind"] in DELIVERY_EVENTS and (moment := cls.moment(row.get("recorded_at"))) and moment >= completion), None)

    @classmethod
    def facts(cls, task: dict) -> list[dict]:
        return sorted(task.get("outcomes", ()), key=lambda row: row.get("recorded_at") or "")

    @classmethod
    def event_key(cls, line: dict, event: dict) -> tuple:
        dimensions = event.get("cohort_dimensions") or {}
        return (*cls.scope_key(line), dimensions.get("model") or "", dimensions.get("tier") or "")

    @classmethod
    def event_cohort(cls, line: dict, event: dict) -> dict:
        dimensions = event.get("cohort_dimensions") or {}
        return {**cls.scope_cohort(line), "model": dimensions.get("model"), "tier": dimensions.get("tier")}

    @staticmethod
    def scope_key(line: dict) -> tuple:
        return (line.get("domain") or "", line.get("size_scale_version") or "", line.get("criteria_version") or "")

    @staticmethod
    def scope_cohort(line: dict) -> dict:
        return {"domain": line.get("domain"), "size_scale_version": line.get("size_scale_version"),
                "criteria_version": line.get("criteria_version")}

    @staticmethod
    def empty_count() -> dict:
        return {"task_count": 0, "size_points": 0, "unknown_size_tasks": 0}

    @staticmethod
    def credit(row: dict, line: dict) -> None:
        row["task_count"] += 1
        if line["size_points"] is None:
            row["unknown_size_tasks"] += 1
        else:
            row["size_points"] += line["size_points"]

    @classmethod
    def available_by(cls, line: dict, after: datetime, sprint_start: datetime) -> bool:
        if line["change_type"] == "baseline":
            return True
        added_at = cls.moment(line.get("recorded_at"))
        if added_at is None:
            return False
        return added_at < after and added_at >= sprint_start

    @classmethod
    def event_day(cls, stamp: str | None, zone: ZoneInfo) -> date | None:
        moment = cls.moment(stamp)
        return moment.astimezone(zone).date() if moment else None

    @staticmethod
    def moment(value: str | None) -> datetime | None:
        if not value:
            return None
        try:
            moment = datetime.fromisoformat(value.replace("Z", "+00:00"))
        except ValueError:
            return None
        return moment.astimezone(timezone.utc) if moment.tzinfo else None

    @staticmethod
    def in_period(moment: datetime, starts_at: datetime, ends_at: datetime) -> bool:
        return starts_at <= moment < ends_at

    @staticmethod
    def size(value: object) -> int | None:
        return value if isinstance(value, int) and not isinstance(value, bool) and value > 0 else None

    @staticmethod
    def line_order(line: dict) -> int:
        return line["task_id"]

    @staticmethod
    def timestamp(value: datetime | None) -> str | None:
        return value.astimezone(timezone.utc).isoformat() if value else None
