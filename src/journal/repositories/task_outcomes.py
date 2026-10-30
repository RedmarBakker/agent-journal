import hashlib
import json

from journal.db.connection import Connection
from journal.events.agent.wait_cleared import WaitCleared
from journal.events.agent.wait_request import WaitRequest
from journal.events.bus import Bus
from journal.events.moments.worker_work_merged import WorkerWorkMerged
from journal.events.rows.row_event import RowEvent
from journal.events.rows.task_closed import TaskClosed
from journal.events.rows.task_reopened import TaskReopened
from journal.events.rows.task_started import TaskStarted
from journal.events.rows.task_test_failed import TaskTestFailed
from journal.events.rows.task_wait_ended import TaskWaitEnded
from journal.events.rows.worker_limited import WorkerLimited
from journal.events.rows.worker_ready import WorkerReady
from journal.events.rows.worker_review_failed import WorkerReviewFailed
from journal.events.rows.worker_review_requested import WorkerReviewRequested
from journal.events.rows.worker_review_undecided import WorkerReviewUndecided
from journal.events.rows.worker_reviewed import WorkerReviewed
from journal.events.rows.worker_spent import WorkerSpent
from journal.events.rows.worker_test_failed import WorkerTestFailed
from journal.features.reviewing.support.point_verdict import PointVerdict
from journal.features.reviewing.support.review_report import ReviewReport
from journal.features.organization.support.organization import Organization
from journal.models.delivery_record import DeliveryRecord
from journal.models.plan import Plan
from journal.models.support.ref import Ref
from journal.models.task import Task
from journal.models.task_outcome import TaskOutcome
from journal.models.worker import Worker
from journal.repositories.domain_rows import DomainRows
from journal.repositories.links import Links
from journal.repositories.plans import PLAN_LINK, Plans
from journal.repositories.scope import Scope
from journal.repositories.scoped_repository import ScopedRepository
from journal.repositories.sprints import SPRINT_PLAN, Sprints
from journal.repositories.task_sizes import TaskSizes
from journal.repositories.tasks import Tasks
from journal.repositories.workers import Workers
from journal.support.actor import Actor
from journal.support.rejection import Rejection
from journal.support.time_source import TimeSource

OUTCOME_TASK_LINK = "task_outcome_task"
OUTCOME_PLAN_LINK = "task_outcome_plan"
OUTCOME_DOMAIN_LINK = "task_outcome_domain"
OUTCOME_COHORT_VERSION = "plan4-outcome-cohort-v1"


class TaskOutcomes(ScopedRepository[TaskOutcome]):
    """The immutable task outcome ledger and its interval and credit projection."""

    model = TaskOutcome

    def __init__(self, connection: Connection, bus: Bus, scope: Scope, time_source: TimeSource, tasks: Tasks, plans: Plans,
                 links: Links, domains: DomainRows, sprints: Sprints, sizes: TaskSizes, organization: Organization,
                 workers: Workers) -> None:
        super().__init__(connection, bus, scope, time_source)
        self.tasks, self.plans, self.links, self.domains = tasks, plans, links, domains
        self.sprints, self.sizes, self.organization, self.workers = sprints, sizes, organization, workers

    def save(self, row: TaskOutcome, actor: Actor) -> TaskOutcome:
        if not row.is_new:
            raise Rejection("task outcome history is immutable")
        return super().save(row, actor)

    def delete(self, row: TaskOutcome, actor: Actor) -> None:
        raise Rejection("task outcome history is immutable")

    def facts(self, task_id: int) -> list[TaskOutcome]:
        task = self.tasks.find(task_id)
        return sorted((self.find(ref.id) for ref in self.links.targets(task, OUTCOME_TASK_LINK)),
                      key=lambda row: (row.occurred_at, row.row_id))

    def record_row_event(self, event: RowEvent) -> TaskOutcome | None:
        if isinstance(event, TaskStarted):
            return self.record_fact(event.task_id, "task_started", event.time,
                                    {"prior_state": event.prior_state, "source_actor": event.actor}, Actor.system(),
                                    self.key("task_started", event.task_id, event.time, event.actor, event.prior_state), event.plan_id)
        if isinstance(event, TaskClosed):
            kind = f"task_{event.outcome}"
            return self.record_fact(event.task_id, kind, event.time,
                                    {"outcome": event.outcome, "worker_id": event.worker_id, "source_actor": event.actor}, Actor.system(),
                                    self.key(kind, event.task_id, event.time, event.actor, event.outcome, event.worker_id))
        if isinstance(event, TaskReopened):
            return self.record_fact(event.task_id, "task_reopened", event.time,
                                    {"reason": event.reason, "source_actor": event.actor}, Actor.system(),
                                    self.key("task_reopened", event.task_id, event.time, event.actor, event.reason))
        if isinstance(event, TaskWaitEnded):
            return self.record_fact(event.task_id, "task_wait_ended", event.time,
                                    {"reason": event.reason, "source_actor": event.actor}, Actor.system(),
                                    self.key("task_wait_ended", event.task_id, event.time, event.actor, event.reason))
        if isinstance(event, TaskTestFailed):
            return self.record_fact(event.task_id, "task_test_failed", event.time,
                                    {"outcome": event.outcome, "output_id": event.output_id, "source_actor": event.actor}, Actor.system(),
                                    self.key("task_test_failed", event.task_id, event.time, event.actor, event.output_id, event.outcome))
        return self.record_worker_event(event)

    def record_worker_event(self, event: RowEvent) -> TaskOutcome | None:
        if isinstance(event, WorkerSpent):
            task_id = self.worker_task(event.worker.id)
            delta = event.cost_dollars - event.before_dollars
            details = {"worker_id": event.worker.id, "model": event.model, "tier": event.tier.value,
                       "profile_tier": event.profile_tier.value, "before_dollars": event.before_dollars,
                       "after_dollars": event.cost_dollars, "cost_delta": delta, "source_actor": event.actor}
            return self.record_fact(task_id, "worker_spent", event.time, details, Actor.system(),
                                    self.key("worker_spent", event.worker.id, event.time, event.model, event.tier.value,
                                             event.profile_tier.value, event.before_dollars, event.cost_dollars))
        if isinstance(event, WorkerLimited):
            task_id = self.worker_task(event.worker.id)
            return self.record_fact(task_id, "usage_limited", event.time,
                                    {"worker_id": event.worker.id, "resumes_at": event.resumes_at, "source_actor": event.actor}, Actor.system(),
                                    self.key("usage_limited", event.worker.id, event.time, event.resumes_at))
        if isinstance(event, WorkerReady):
            task_id = self.worker_task(event.worker.id)
            return self.record_fact(task_id, "usage_resumed", event.time,
                                    {"worker_id": event.worker.id, "source_actor": event.actor}, Actor.system(),
                                    self.key("usage_resumed", event.worker.id, event.time))
        if isinstance(event, WorkerTestFailed):
            task_id = self.worker_task(event.worker.id)
            return self.record_fact(task_id, "worker_test_failed", event.time,
                                    {"worker_id": event.worker.id, "failed": event.failed, "runs": event.runs,
                                     "source_actor": event.actor}, Actor.system(),
                                    self.key("worker_test_failed", event.worker.id, event.time, event.failed, event.runs))
        if isinstance(event, WorkerReviewRequested):
            return self.record_fact(self.worker_task(event.worker.id), "review_started", event.time,
                                    {"worker_id": event.worker.id, "report": event.report, "source_actor": event.actor}, Actor.system(),
                                    self.key("review_started", event.worker.id, event.time, event.report))
        if isinstance(event, WorkerReviewFailed):
            kind, details = "review_failed", {"worker_id": event.worker.id, "outcome": event.outcome, "source_actor": event.actor}
            return self.record_fact(event.task, kind, event.time, details, Actor.system(),
                                    self.key(kind, event.task, event.worker.id, event.time, event.outcome))
        if isinstance(event, WorkerReviewed):
            report = ReviewReport(event.report)
            task = self.tasks.find(event.task)
            short_points = [{"number": point.number, "reason": point.reason} for point in report.judged(PointVerdict.SHORT)]
            undecided_points = [{"number": point.number, "reason": point.reason} for point in report.judged(PointVerdict.UNDECIDED)]
            kind = "review_sent_back" if short_points else "review_undecided" if undecided_points or report.is_undecided(len(task.points())) else "review_completed"
            details = {"worker_id": event.worker.id, "reviewer_id": event.reviewer, "report": event.report,
                       "short_points": short_points, "undecided_points": undecided_points, "source_actor": event.actor}
            return self.record_fact(event.task, kind, event.time, details, Actor.system(),
                                    self.key(kind, event.task, event.worker.id, event.time, event.reviewer, event.report))
        if isinstance(event, WorkerReviewUndecided):
            return None
        return None

    def record_wait_request(self, event: WaitRequest) -> TaskOutcome | None:
        task = self.tasks.current(event.agent)
        if task is None:
            return None
        return self.record_fact(task.row_id, "user_wait_started", event.time,
                                {"focus": event.focus, "end_refs": event.end_refs, "source_actor": f"agent:{event.session}"}, Actor.system(),
                                self.key("user_wait_started", task.row_id, event.session, event.time, event.focus, event.end_refs),
                                agent_session=event.session)

    def record_wait_cleared(self, event: WaitCleared) -> TaskOutcome | None:
        starts = self.matching(agent_session=event.session, kind="user_wait_started")
        closed = {row.details.get("start_fact_id") for row in self.matching(agent_session=event.session, kind="user_wait_ended")}
        start = next((row for row in sorted(starts, key=lambda item: (item.occurred_at, item.row_id), reverse=True) if row.row_id not in closed), None)
        if start is None:
            return None
        details = {"start_fact_id": start.row_id, "focus": start.details.get("focus", ""),
                   "end_refs": start.details.get("end_refs", ""), "source_actor": f"agent:{event.session}"}
        return self.record_fact(start.task_id, "user_wait_ended", event.time, details, Actor.system(),
                                self.key("user_wait_ended", start.row_id, event.session, event.time), agent_session=event.session)

    def record_merge(self, event: WorkerWorkMerged) -> TaskOutcome:
        return self.record_fact(event.task, "worker_work_merged", event.time,
                                {"worker_id": event.worker, "worker_name": event.name, "lines": event.lines,
                                 "merged_shas": list(event.merged_shas), "source_actor": Actor.system().stamp}, Actor.system(),
                                self.key("worker_work_merged", event.task, event.worker, event.time, event.merged_shas))

    def record_delivery(self, plan: Plan, tasks: list[Task], row: DeliveryRecord, actor: Actor) -> None:
        kind = "delivery_proposed" if row.state == "proposed" else "delivery_reopened" if row.state == "reopened" else "delivery_corrected" if row.generation > 1 else "delivery_accepted"
        for task in tasks:
            details = {"delivery_id": row.row_id, "state": row.state, "generation": row.generation,
                       "assurance": row.assurance, "evidence": row.evidence, "reason": row.reason}
            self.record_fact(task.row_id, kind, self.time_source.seconds(), details, actor,
                             f"delivery:{row.row_id}:task:{task.row_id}", plan.row_id, row.policy_version, row.generation)

    def record_fact(self, task_id: int, kind: str, occurred_at: float, details: dict, actor: Actor, event_key: str,
                    plan_id: int = 0, policy_version: str = "", delivery_generation: int = 0,
                    agent_session: str = "") -> TaskOutcome | None:
        if not task_id:
            return None
        with self.writing():
            existing = self.matching(event_key=event_key)
            if existing:
                return existing[0]
            task = self.tasks.find(task_id)
            plan = self.task_plan(task, plan_id)
            snapshot = self.sprints.committed_task_snapshot(plan, task.row_id) if plan else None
            sizing = self.sizes.show(task.row_id)
            domain_name = snapshot.get("domain") if snapshot else self.domains.planned_domain_name(task)
            domain = self.organization.contracts().domain(domain_name) if domain_name else None
            definition = domain.definition_of_done if domain else None
            version = policy_version or (snapshot.get("criteria_version") if snapshot else definition.version if definition else "") or ""
            baseline_size = sizing.get("planning_baseline_size")
            committed_size = snapshot.get("size") if snapshot else None
            planned_size = snapshot.get("size") if snapshot else baseline_size
            first_ready = sizing.get("first_ready_size")
            scope_added = self.scope_added(plan, task, snapshot)
            capacity = self.sprints.plan_snapshot(plan).get("capacity_assumptions") if plan else None
            missing = self.missing_measurements(task, plan, domain_name, version, planned_size, capacity)
            cohort = self.cohort_data(task, domain_name, version, snapshot, sizing, details)
            recorded_details = {**details, "capacity_assumptions": capacity, "missing_measurements": missing, "cohort": cohort}
            row = self.save(TaskOutcome(environment_id=task.environment_id, kind=kind, event_key=event_key, task_id=task.row_id,
                                        plan_id=plan.row_id if plan else 0, domain_name=domain_name or "", policy_version=version,
                                        cohort_version=OUTCOME_COHORT_VERSION, cohort_key=cohort["key"],
                                        occurred_at=occurred_at, planning_baseline_size=baseline_size, planned_size=planned_size,
                                        first_ready_size=first_ready, committed_size=committed_size,
                                        final_size=task.size, scope_added=scope_added, delivery_generation=delivery_generation,
                                        agent_session=agent_session, details=recorded_details), actor)
            self.links.linked(Ref.build(task), Ref.build(row), OUTCOME_TASK_LINK, actor)
            if plan:
                self.links.linked(Ref.build(plan), Ref.build(row), OUTCOME_PLAN_LINK, actor)
            if domain_name:
                domain_row = self.domains.named(domain_name, actor)
                self.links.linked(Ref.build(domain_row), Ref.build(row), OUTCOME_DOMAIN_LINK, actor)
            return row

    def summary(self, task_id: int, as_of: float | None = None) -> dict:
        facts = self.facts(task_id)
        now = self.time_source.seconds() if as_of is None else as_of
        intervals = self.intervals(facts, now)
        active_intervals = self.active_intervals(facts, now)
        execution = self.execution_status(facts)
        delivery = [row for row in facts if row.kind in ("delivery_accepted", "delivery_corrected", "delivery_reopened")]
        delivery_status = delivery[-1].kind if delivery else "awaiting_delivery" if any(row.kind in ("task_completed", "worker_work_merged") for row in facts) else "not_started"
        delivered = delivery_status in ("delivery_accepted", "delivery_corrected")
        planned_size = next((row.planned_size for row in reversed(facts) if row.planned_size is not None), None)
        baseline_size = next((row.planning_baseline_size for row in reversed(facts) if row.planning_baseline_size is not None), None)
        first_ready_size = next((row.first_ready_size for row in reversed(facts) if row.first_ready_size is not None), None)
        committed_size = next((row.committed_size for row in reversed(facts) if row.committed_size is not None), None)
        final_size = next((row.final_size for row in reversed(facts) if row.final_size is not None), None)
        scope_added = next((row.scope_added for row in reversed(facts) if row.scope_added is not None), None)
        capacity = next((row.details.get("capacity_assumptions") for row in reversed(facts) if row.details.get("capacity_assumptions") is not None), None)
        waits = [interval for interval in intervals if interval["kind"] in ("task_wait", "user_wait", "usage_limit", "review_wait", "delivery_wait")]
        credits = planned_size if delivered and scope_added is False else None
        costs = [row for row in facts if row.kind == "worker_spent"]
        has_delivery_wait = any(row.kind in ("task_completed", "worker_work_merged", "delivery_reopened", "delivery_accepted", "delivery_corrected") for row in facts)
        return {"task_id": task_id, "plan_id": self.plan_id(facts), "domain": self.domain_name(facts),
                "policy_version": self.policy_version(facts), "execution_status": execution,
                "artifact_accepted": any(row.kind == "worker_work_merged" for row in facts), "delivery_accepted": delivered,
                "delivery_status": delivery_status, "right_censored": execution not in ("completed", "cancelled") or any(row["end"] is None for row in waits),
                "planning_baseline_size": baseline_size, "planned_size": planned_size, "first_ready_size": first_ready_size,
                "committed_size": committed_size, "final_size": final_size, "scope_added": scope_added,
                "capacity_assumptions": capacity, "missing_measurements": self.missing_from(facts),
                "delivery_generations": [row.delivery_generation for row in delivery if row.delivery_generation],
                "credited_points": credits,
                "active_seconds": sum(row["duration_seconds"] for row in active_intervals) if any(row.kind == "task_started" for row in facts) else None,
                "active_time_right_censored": any(row["end"] is None for row in active_intervals),
                "cost_dollars": sum(row.details.get("cost_delta", 0.0) for row in costs) if costs else None,
                "worker_costs": [row.details for row in costs],
                "wait_intervals": intervals, "waiting_seconds": self.union_seconds(waits),
                "task_wait_seconds": self.seconds_of(intervals, "task_wait"),
                "user_wait_seconds": self.seconds_of(intervals, "user_wait"),
                "usage_wait_seconds": self.seconds_of(intervals, "usage_limit"),
                "review_wait_seconds": self.seconds_of(intervals, "review_wait"),
                "delivery_wait_seconds": self.seconds_of(intervals, "delivery_wait") if has_delivery_wait else None}

    def intervals(self, facts: list[TaskOutcome], now: float) -> list[dict]:
        intervals: list[dict] = []
        active: dict[tuple[str, str], dict] = {}
        for row in facts:
            details = row.details
            if row.kind in ("task_paused", "task_blocked", "task_testing"):
                self.open_interval(active, "task_wait", "", row.occurred_at, None)
            elif row.kind == "task_test_failed":
                self.close_interval(active, "task_wait", "", row.occurred_at, intervals)
                self.open_interval(active, "task_wait", "", row.occurred_at, None)
            elif row.kind in ("task_started", "task_reopened", "task_wait_ended"):
                self.close_interval(active, "task_wait", "", row.occurred_at, intervals)
            elif row.kind == "user_wait_started":
                self.open_interval(active, "user_wait", row.agent_session, row.occurred_at, None)
            elif row.kind == "user_wait_ended":
                self.close_interval(active, "user_wait", row.agent_session, row.occurred_at, intervals)
            elif row.kind == "usage_limited":
                worker = str(details.get("worker_id", ""))
                self.open_interval(active, "usage_limit", worker, row.occurred_at, details.get("resumes_at"))
            elif row.kind == "usage_resumed":
                self.close_interval(active, "usage_limit", str(details.get("worker_id", "")), row.occurred_at, intervals)
            elif row.kind == "review_started":
                self.open_interval(active, "review_wait", str(details.get("worker_id", "")), row.occurred_at, None)
            elif row.kind in ("review_completed", "review_failed", "review_sent_back", "review_undecided"):
                self.close_interval(active, "review_wait", str(details.get("worker_id", "")), row.occurred_at, intervals)
            elif row.kind in ("task_completed", "worker_work_merged", "delivery_reopened"):
                self.open_interval(active, "delivery_wait", "", row.occurred_at, None)
            elif row.kind in ("delivery_accepted", "delivery_corrected"):
                self.close_interval(active, "delivery_wait", "", row.occurred_at, intervals)
        intervals.extend({**interval, "end": None, "duration_seconds": max(0, now - interval["start"]), "right_censored": True}
                         for interval in active.values())
        return sorted(intervals, key=lambda row: (row["start"], row["kind"]))

    def execution_status(self, facts: list[TaskOutcome]) -> str:
        statuses = {"task_started": "in_progress", "task_paused": "paused", "task_blocked": "blocked", "task_testing": "testing",
                    "task_completed": "completed", "task_cancelled": "cancelled", "task_reopened": "open", "task_test_failed": "paused"}
        return next((statuses[row.kind] for row in reversed(facts) if row.kind in statuses), "open")

    def active_intervals(self, facts: list[TaskOutcome], now: float) -> list[dict]:
        intervals: list[dict] = []
        active_at: float | None = None
        for row in facts:
            if row.kind == "task_started" and active_at is None:
                active_at = row.occurred_at
            elif row.kind in ("task_paused", "task_blocked", "task_testing", "task_completed", "task_cancelled") and active_at is not None:
                intervals.append({"start": active_at, "end": row.occurred_at,
                                  "duration_seconds": max(0, row.occurred_at - active_at), "right_censored": False})
                active_at = None
        if active_at is not None:
            intervals.append({"start": active_at, "end": None,
                              "duration_seconds": max(0, now - active_at), "right_censored": True})
        return intervals

    def task_plan(self, task: Task, plan_id: int = 0) -> Plan | None:
        if plan_id:
            return self.plans.find(plan_id)
        ref = next((ref for ref in self.links.targets(task, PLAN_LINK) if ref.type == Plan.table()), None)
        return self.plans.find(ref.id) if ref else None

    def scope_added(self, plan: Plan | None, task: Task, snapshot: dict | None) -> bool | None:
        if plan is None or not self.links.sources(plan, SPRINT_PLAN):
            return None
        return snapshot is None

    def missing_measurements(self, task: Task, plan: Plan | None, domain_name: str | None, version: str,
                            planned_size: int | None, capacity: object) -> list[str]:
        values = {"plan": plan, "domain": domain_name, "domain_policy_version": version,
                  "planned_size": planned_size, "final_size": task.size, "capacity_assumptions": capacity}
        return [name for name, value in values.items() if value is None or value == ""]

    def cohort_data(self, task: Task, domain_name: str | None, version: str, snapshot: dict | None,
                    sizing: dict, details: dict) -> dict:
        history = sizing["history"]
        size_version = snapshot.get("size_scale_version") if snapshot else history[0]["scale_version"] if history else sizing["current_scale_version"]
        dimensions = {"environment_id": task.environment_id, "domain": domain_name, "size_scale_version": size_version,
                      "criteria_version": version or None, "model": details.get("model"), "tier": details.get("tier")}
        return {"version": OUTCOME_COHORT_VERSION, "key": self.cohort_key(dimensions), "dimensions": dimensions}

    def missing_from(self, facts: list[TaskOutcome]) -> list[str]:
        return sorted({name for row in facts for name in row.details.get("missing_measurements", ())})

    def plan_id(self, facts: list[TaskOutcome]) -> int:
        return next((row.plan_id for row in reversed(facts) if row.plan_id), 0)

    def domain_name(self, facts: list[TaskOutcome]) -> str:
        return next((row.domain_name for row in reversed(facts) if row.domain_name), "")

    def policy_version(self, facts: list[TaskOutcome]) -> str:
        return next((row.policy_version for row in reversed(facts) if row.policy_version), "")

    def worker_task(self, worker_id: int) -> int:
        holder = self.tasks.holder_task(Ref(Worker.table(), worker_id))
        if holder:
            return holder.row_id
        worker = self.workers.find(worker_id)
        return worker.merged_task or worker.edited_task

    def open_interval(self, active: dict, kind: str, key: str, start: float, expected_end: float | None) -> None:
        active.setdefault((kind, key), {"kind": kind, "start": start, "expected_end": expected_end})

    def close_interval(self, active: dict, kind: str, key: str, end: float, intervals: list[dict]) -> None:
        if interval := active.pop((kind, key), None):
            intervals.append({**interval, "end": end, "duration_seconds": max(0, end - interval["start"]), "right_censored": False})

    @staticmethod
    def seconds_of(intervals: list[dict], kind: str) -> float:
        return sum(interval["duration_seconds"] for interval in intervals if interval["kind"] == kind)

    @staticmethod
    def union_seconds(intervals: list[dict]) -> float:
        ranges = sorted((row["start"], row["start"] + row["duration_seconds"]) for row in intervals)
        total = 0.0
        start = end = None
        for next_start, next_end in ranges:
            if start is None:
                start, end = next_start, next_end
            elif next_start <= end:
                end = max(end, next_end)
            else:
                total += end - start
                start, end = next_start, next_end
        return total + (end - start if start is not None else 0)

    @staticmethod
    def key(kind: str, *parts) -> str:
        encoded = json.dumps(parts, sort_keys=True, default=str, separators=(",", ":"))
        return f"{kind}:{hashlib.sha256(encoded.encode()).hexdigest()}"

    @staticmethod
    def cohort_key(dimensions: dict) -> str:
        encoded = json.dumps(dimensions, sort_keys=True, separators=(",", ":"))
        return f"{OUTCOME_COHORT_VERSION}:{hashlib.sha256(encoded.encode()).hexdigest()}"
