from datetime import datetime, timezone

from journal.features.estimates.estimates_options import EstimatesOptions
from journal.features.plans.support.plan_owners import PlanOwners
from journal.models.delivery_record import DeliveryRecord
from journal.models.link import Link
from journal.models.plan import Plan
from journal.models.support.ref import Ref
from journal.models.sprint import Sprint
from journal.models.sprint_change import SprintChange
from journal.models.sprint_commitment import SprintCommitment
from journal.models.task import Task
from journal.models.task_outcome import TaskOutcome
from journal.repositories.delivery_records import DeliveryRecords
from journal.repositories.links import Links
from journal.repositories.plans import Plans
from journal.repositories.setting_rows import SettingRows
from journal.repositories.sprint_changes import SprintChanges
from journal.repositories.sprint_commitments import SprintCommitments
from journal.repositories.sprints import CHANGE_PLAN, COMMITMENT_PLAN, SPRINT_CHANGE, SPRINT_COMMITMENT, SPRINT_PLAN, Sprints
from journal.repositories.task_outcomes import OUTCOME_PLAN_LINK, TaskOutcomes
from journal.repositories.task_sizes import TaskSizes
from journal.repositories.tasks import Tasks
from journal.support.actor import Actor
from journal.support.rejection import Rejection


PLAN_OUTCOME_HISTORY_VERSION = "plan-outcome-history-v1"


class PlanOutcomeHistory:
    """The owner-scoped read projection of one plan's durable estimates, commitments and outcomes."""

    def __init__(self, plans: Plans, owners: PlanOwners, links: Links, sprints: Sprints, commitments: SprintCommitments,
                 changes: SprintChanges, sizes: TaskSizes, outcomes: TaskOutcomes, delivery: DeliveryRecords,
                 tasks: Tasks, settings: SettingRows) -> None:
        self.plans, self.owners, self.links, self.sprints = plans, owners, links, sprints
        self.commitments, self.changes, self.sizes, self.outcomes = commitments, changes, sizes, outcomes
        self.delivery, self.tasks, self.settings = delivery, tasks, settings

    def read(self, plan_id: int, actor: Actor) -> dict:
        plan = self.plans.find(plan_id)
        self.owner(plan, actor)
        sprint_history = self.sprint_history(plan)
        delivery_rows = self.delivery.plan_records(plan)
        tasks = self.history_tasks(plan, sprint_history)
        current_task_ids = {task.row_id for task in self.plans.plan_tasks(plan)}
        task_history = [self.task_history(plan, task, delivery_rows, task.row_id in current_task_ids) for task in tasks]
        delivery_tasks = [self.delivery.task_data(plan, task, delivery_rows) for task in self.plans.plan_tasks(plan)]
        capacity = self.capacity(sprint_history, plan)
        flags = [{"task_id": task["task_id"], **flag} for task in task_history for flag in task["data_quality"]["flags"]]
        if capacity in (None, {}):
            flags.append({"name": "capacity", "status": "not_measured", "reason": "No capacity assumptions or daily availability observations are recorded."})
        return {"schema_version": PLAN_OUTCOME_HISTORY_VERSION,
                "scope": {"environment_id": plan.environment_id, "plan_id": plan.row_id, "plan_title": plan.title,
                          "plan_state": plan.state.value, "plan_mode": plan.mode.value},
                "estimates_mode": str(self.settings.option(EstimatesOptions.MODE)),
                "availability": {"status": "recorded" if capacity not in (None, {}) else "not_measured",
                                 "capacity_assumptions": capacity, "daily_observations": None},
                "sprints": sprint_history,
                "tasks": task_history,
                "delivery": {"status": self.delivery.plan_status(delivery_tasks), "tasks": delivery_tasks,
                             "history": [self.delivery.history_data(row) for row in delivery_rows]},
                "data_quality": {"status": "incomplete" if flags else "complete", "flags": flags}}

    def history_tasks(self, plan: Plan, sprints: list[dict]) -> list[Task]:
        task_ids = {task.row_id for task in self.plans.plan_tasks(plan)}
        for sprint in sprints:
            for commitment in sprint["commitments"]:
                task_ids.update(task["id"] for task in commitment["snapshot"].get("tasks", ())
                                if isinstance(task, dict) and isinstance(task.get("id"), int))
            for change in sprint["changes"]:
                task_ids.update(task["id"] for task in change["data"].get("tasks", ())
                                if isinstance(task, dict) and isinstance(task.get("id"), int))
        task_ids.update(self.outcomes.find(ref.id).task_id for ref in self.links.targets(plan, OUTCOME_PLAN_LINK))
        return [self.tasks.find(task_id) for task_id in sorted(task_ids)]

    def task_history(self, plan: Plan, task: Task, delivery_rows: list[DeliveryRecord], current_in_plan: bool) -> dict:
        facts = self.outcomes.facts(task.row_id)
        summary = self.outcomes.summary(task.row_id)
        task_delivery = self.delivery.task_data(plan, task, delivery_rows)
        starts = [row for row in facts if row.kind == "task_started"]
        reliable_start = bool(starts) and all(row.occurred_at > 0 for row in starts)
        active = summary["active_seconds"] if reliable_start else None
        cost = summary["cost_dollars"]
        accepted = task_delivery["status"] == "delivered"
        delivery_at = self.delivery_time(task, delivery_rows) if accepted else None
        wait_intervals = [row for row in summary["wait_intervals"]
                          if row["kind"] != "delivery_wait" and row["start"] > 0 and (row["end"] is None or row["end"] > 0)]
        wait_seconds = self.outcomes.union_seconds(wait_intervals) if wait_intervals else None
        delivery_events = [row for row in facts if row.kind in ("task_completed", "worker_work_merged", "delivery_reopened", "delivery_accepted", "delivery_corrected")]
        delivery_wait = summary["delivery_wait_seconds"] if delivery_events and all(row.occurred_at > 0 for row in delivery_events) else None
        measurements = {"active_time": {"status": "measured" if active is not None else "not_measured", "seconds": active},
                        "block_and_wait_time": {"status": "measured" if wait_intervals else "not_measured",
                                                 "seconds": wait_seconds, "intervals": wait_intervals or None},
                        "cost": {"status": "measured" if cost is not None else "not_measured",
                                 "label": "Measured" if cost is not None else "Not measured", "amount_dollars": cost},
                        "delivery": {"status": "evidenced" if accepted else "not_evidenced", "accepted_at": delivery_at,
                                     "evidence_time_status": "measured" if delivery_at else "not_measured",
                                     "wait_status": "measured" if delivery_wait is not None else "not_measured",
                                     "wait_seconds": delivery_wait}}
        execution = self.execution_data(task, facts, summary, wait_intervals, accepted, task_delivery, active, reliable_start, delivery_wait)
        estimate_history = self.sizes.show(task.row_id)
        flags = self.task_flags(facts, measurements, estimate_history)
        return {"task_id": task.row_id, "title": task.title, "current_in_plan": current_in_plan, "estimate_history": estimate_history,
                "execution": execution, "outcomes": [self.outcome_data(row) for row in facts], "delivery": task_delivery,
                "measurements": measurements, "data_quality": {"status": "incomplete" if flags else "complete", "flags": flags}}

    def execution_data(self, task: Task, facts: list[TaskOutcome], summary: dict, wait_intervals: list[dict], accepted: bool,
                       delivery: dict, active: float | None, reliable_start: bool, delivery_wait: float | None) -> dict:
        waits = {kind: self.outcomes.seconds_of(wait_intervals, kind) if any(row["kind"] == kind for row in wait_intervals) else None
                 for kind in ("task_wait", "user_wait", "usage_limit", "review_wait")}
        lifecycle = any(row.kind in ("task_started", "task_paused", "task_blocked", "task_testing", "task_completed", "task_cancelled", "task_reopened") for row in facts)
        return {**summary, "history_status": "recorded" if lifecycle else "not_measured", "current_task_state": task.state.value,
                "execution_status": summary["execution_status"] if lifecycle else None,
                "artifact_accepted": summary["artifact_accepted"] if lifecycle else None, "delivery_accepted": accepted,
                "delivery_status": delivery["status"], "right_censored": summary["right_censored"] if lifecycle else None,
                "active_seconds": active, "active_time_right_censored": summary["active_time_right_censored"] if reliable_start else None,
                "delivery_wait_seconds": delivery_wait,
                "wait_intervals": wait_intervals or None, "waiting_seconds": self.outcomes.union_seconds(wait_intervals) if wait_intervals else None,
                "task_wait_seconds": waits["task_wait"], "user_wait_seconds": waits["user_wait"],
                "usage_wait_seconds": waits["usage_limit"], "review_wait_seconds": waits["review_wait"]}

    def sprint_history(self, plan: Plan) -> list[dict]:
        sprints = [self.sprints.find(ref.id) for ref in self.links.sources(plan, SPRINT_PLAN)]
        return [self.sprint_data(sprint, plan) for sprint in sorted(sprints, key=lambda row: (row.starts_at, row.row_id))]

    def sprint_data(self, sprint: Sprint, plan: Plan) -> dict:
        membership = next((link for link in self.links.source_links(sprint, SPRINT_PLAN) if link.target == Ref.build(plan)), None)
        commitments = [self.commitments.find(ref.id) for ref in self.links.targets(sprint, SPRINT_COMMITMENT)]
        commitments = [row for row in commitments if Ref.build(plan) in self.links.targets(row, COMMITMENT_PLAN)]
        changes = [self.changes.find(ref.id) for ref in self.links.targets(sprint, SPRINT_CHANGE)]
        changes = [row for row in changes if Ref.build(plan) in self.links.targets(row, CHANGE_PLAN)]
        return {"id": sprint.row_id, "starts_on": sprint.starts_on, "ends_on": sprint.ends_on,
                "starts_at": self.timestamp(sprint.starts_at), "ends_at": self.timestamp(sprint.ends_at),
                "timezone": sprint.timezone, "length_days": sprint.length_days, "calendar_version": sprint.calendar_version,
                "state": sprint.state.value, "actor": self.actor(sprint), "recorded_at": self.timestamp(sprint.created_at),
                "membership": self.link_data(membership), "commitments": [self.commitment_data(row) for row in commitments],
                "changes": [self.change_data(row) for row in changes]}

    def commitment_data(self, row: SprintCommitment) -> dict:
        return {"id": row.row_id, "snapshot": row.snapshot, "actor": self.actor(row), "recorded_at": self.timestamp(row.created_at)}

    def change_data(self, row: SprintChange) -> dict:
        return {"id": row.row_id, "change_type": row.change_type, "reason": row.reason, "data": row.data,
                "actor": self.actor(row), "recorded_at": self.timestamp(row.created_at)}

    def outcome_data(self, row: TaskOutcome) -> dict:
        cohort = row.details.get("cohort") or {}
        return {"id": row.row_id, "kind": row.kind, "event_key": row.event_key, "actor": self.actor(row),
                "source_actor": row.details.get("source_actor"), "recorded_at": self.timestamp(row.created_at),
                "occurred_at": self.timestamp(row.occurred_at) if row.occurred_at > 0 else None,
                "planning_baseline_size": row.planning_baseline_size, "planned_size": row.planned_size,
                "first_ready_size": row.first_ready_size, "committed_size": row.committed_size, "final_size": row.final_size,
                "scope_added": row.scope_added, "policy_version": row.policy_version,
                "cohort_version": row.cohort_version, "cohort_key": row.cohort_key,
                "cohort_dimensions": cohort.get("dimensions"), "details": row.details}

    def task_flags(self, facts: list[TaskOutcome], measurements: dict, estimate_history: dict) -> list[dict]:
        flags = []
        if measurements["active_time"]["status"] == "not_measured":
            flags.append({"name": "active_time", "status": "not_measured", "reason": "No reliable task start fact is recorded."})
        if not any(row.kind in ("task_started", "task_paused", "task_blocked", "task_testing", "task_completed", "task_cancelled", "task_reopened") for row in facts):
            flags.append({"name": "execution_history", "status": "not_measured", "reason": "No reliable task lifecycle fact is recorded."})
        if measurements["block_and_wait_time"]["status"] == "not_measured":
            flags.append({"name": "block_history", "status": "not_measured", "reason": "No durable block or wait facts are recorded."})
        if measurements["cost"]["status"] == "not_measured":
            flags.append({"name": "cost", "status": "not_measured", "reason": "No worker cost facts are recorded."})
        if measurements["delivery"]["status"] == "not_evidenced":
            flags.append({"name": "delivery_evidence", "status": "not_evidenced", "reason": "No currently accepted domain evidence is recorded."})
        elif measurements["delivery"]["evidence_time_status"] == "not_measured":
            flags.append({"name": "delivery_timestamp", "status": "incomplete", "reason": "Accepted domain evidence has no reliable delivery time."})
        if not estimate_history["history"]:
            flags.append({"name": "estimate_history", "status": "not_measured", "reason": "No accepted estimate history is recorded."})
        if any(row.occurred_at <= 0 for row in facts):
            flags.append({"name": "outcome_timestamp", "status": "incomplete", "reason": "At least one outcome has no reliable occurrence time."})
        if any(not row.cohort_version or not row.cohort_key for row in facts):
            flags.append({"name": "cohort_key", "status": "incomplete", "reason": "At least one outcome has no versioned cohort key."})
        return flags

    def delivery_time(self, task: Task, rows: list[DeliveryRecord]) -> str | None:
        current = self.delivery.current_delivery(rows, task)
        if current is None or current.state != "accepted":
            return None
        occurred_at = current.evidence.get("occurred_at")
        return occurred_at if isinstance(occurred_at, str) and occurred_at else None

    def capacity(self, sprints: list[dict], plan: Plan) -> object:
        capacity = next((commitment["snapshot"].get("capacity_assumptions") for sprint in reversed(sprints)
                         for commitment in sprint["commitments"] if commitment["snapshot"].get("capacity_assumptions") is not None), None)
        return capacity if capacity is not None else self.sprints.plan_snapshot(plan).get("capacity_assumptions")

    def link_data(self, row: Link | None) -> dict | None:
        if row is None:
            return None
        return {"actor": self.actor(row), "recorded_at": self.timestamp(row.created_at)}

    def owner(self, plan: Plan, actor: Actor) -> None:
        if not actor.is_user() or self.owners.number(plan) != actor.number():
            raise Rejection("only the plan owner may read plan outcome history")

    @staticmethod
    def actor(row) -> str:
        return row.creator.stamp if row.creator else ""

    @staticmethod
    def timestamp(moment: datetime | float | None) -> str | None:
        if isinstance(moment, datetime):
            return moment.astimezone(timezone.utc).isoformat()
        if isinstance(moment, (int, float)) and moment > 0:
            return datetime.fromtimestamp(moment, timezone.utc).isoformat()
        return None
