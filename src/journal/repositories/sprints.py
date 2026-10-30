from datetime import date, datetime, time, timedelta, timezone
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from journal.db.connection import Connection
from journal.events.bus import Bus
from journal.features.estimates.estimates_options import EstimatesOptions
from journal.models.link import Link
from journal.models.plan import Plan
from journal.models.sprint import Sprint
from journal.models.sprint_change import SprintChange
from journal.models.sprint_commitment import SprintCommitment
from journal.models.sprint_state import SprintState
from journal.features.organization.support.organization import Organization
from journal.models.support.ref import Ref
from journal.models.task import Task
from journal.repositories.domain_rows import DomainRows
from journal.repositories.links import Links
from journal.repositories.plans import Plans
from journal.repositories.scope import Scope
from journal.repositories.scoped_repository import ScopedRepository
from journal.repositories.sprint_changes import SprintChanges
from journal.repositories.sprint_commitments import SprintCommitments
from journal.repositories.tasks import Tasks
from journal.repositories.setting_rows import SettingRows
from journal.support.actor import Actor
from journal.support.caller import LOCAL_USER
from journal.support.rejection import Rejection
from journal.support.time_source import TimeSource

SPRINT_PLAN = "sprint_plan"
SPRINT_COMMITMENT = "sprint_commitment"
COMMITMENT_PLAN = "commitment_plan"
SPRINT_CHANGE = "sprint_change"
CHANGE_PLAN = "change_plan"
CHANGE_NEXT_SPRINT = "change_next_sprint"


class Sprints(ScopedRepository[Sprint]):
    model = Sprint

    def __init__(self, connection: Connection, bus: Bus, scope: Scope, time_source: TimeSource, settings: SettingRows,
                 plans: Plans, tasks: Tasks, domains: DomainRows, links: Links, commitments: SprintCommitments,
                 changes: SprintChanges, organization: Organization) -> None:
        super().__init__(connection, bus, scope, time_source)
        self.settings, self.plans, self.tasks, self.domains = settings, plans, tasks, domains
        self.links, self.commitments, self.changes = links, commitments, changes
        self.organization = organization

    def create(self, starts_on: str, timezone_name: str, actor: Actor) -> Sprint:
        self.owner(actor)
        length_days = self.settings.integer(EstimatesOptions.SPRINT_LENGTH_DAYS)
        starts_at, ends_at, ends_on = self.period(starts_on, timezone_name, length_days)
        self.no_overlap(starts_at, ends_at)
        version = self.calendar_version(length_days, timezone_name)
        return self.save(Sprint(starts_on=starts_on, ends_on=ends_on, starts_at=starts_at, ends_at=ends_at,
                                timezone=timezone_name, length_days=length_days, calendar_version=version), actor)

    def change_calendar(self, sprint_id: int, starts_on: str, timezone_name: str, length_days: int | None, actor: Actor) -> Sprint:
        self.owner(actor)
        sprint = self.find(sprint_id)
        if sprint.state != SprintState.DRAFT:
            raise Rejection("an active sprint's calendar boundaries are frozen; only draft sprints can change")
        length = length_days if length_days is not None else sprint.length_days
        starts_at, ends_at, ends_on = self.period(starts_on, timezone_name, length)
        self.no_overlap(starts_at, ends_at, sprint.row_id)
        version = self.changed_calendar_version(sprint, length, timezone_name)
        return self.save(sprint.with_(starts_on=starts_on, ends_on=ends_on, starts_at=starts_at, ends_at=ends_at,
                                      timezone=timezone_name, length_days=length, calendar_version=version), actor)

    def assign(self, sprint_id: int, plan_id: int, reason: str, actor: Actor) -> Sprint:
        self.owner(actor)
        sprint, plan = self.find(sprint_id), self.plans.find(plan_id)
        self.require_membership_open(sprint)
        if self.has_plan(sprint, plan):
            return sprint
        self.no_other_current_membership(sprint, plan)
        if sprint.state == SprintState.ACTIVE and not reason.strip():
            raise Rejection("a post-start membership change needs a reason")
        with self.writing():
            self.links.linked(Ref.build(sprint), Ref.build(plan), SPRINT_PLAN, actor)
            if sprint.state == SprintState.ACTIVE:
                self.record_change(sprint, plan, "plan_added", reason, self.plan_snapshot(plan), actor)
        return sprint

    def start(self, sprint_id: int, actor: Actor) -> Sprint:
        self.owner(actor)
        sprint = self.find(sprint_id)
        if sprint.state == SprintState.ACTIVE:
            return sprint
        if sprint.state != SprintState.DRAFT:
            raise Rejection("a closed sprint cannot be started again")
        if any(period.state == SprintState.ACTIVE for period in self.rows()):
            raise Rejection("another sprint is already active")
        with self.writing():
            for plan in self.plans_in(sprint):
                self.record_commitment(sprint, plan, actor)
            return self.save(sprint.activated(), actor)

    def close(self, sprint_id: int, actor: Actor) -> Sprint:
        self.owner(actor)
        sprint = self.find(sprint_id)
        if sprint.state == SprintState.CLOSED:
            return sprint
        if sprint.state != SprintState.ACTIVE:
            raise Rejection("only an active sprint can be closed")
        return self.save(sprint.closed(self.time_source.seconds()), actor)

    def carry(self, sprint_id: int, plan_id: int, next_sprint_id: int, reason: str, actor: Actor) -> Sprint:
        self.owner(actor)
        sprint, plan = self.find(sprint_id), self.plans.find(plan_id)
        if sprint.state != SprintState.CLOSED or not self.has_plan(sprint, plan):
            raise Rejection("carry-over needs a plan in a closed sprint")
        if not reason.strip():
            raise Rejection("carry-over needs a reason")
        next_sprint = self.find(next_sprint_id) if next_sprint_id else None
        if next_sprint:
            self.require_membership_open(next_sprint)
            if next_sprint.starts_at < sprint.ends_at:
                raise Rejection("carry-over must go to a sprint after the closed period")
            if self.has_plan(next_sprint, plan):
                return sprint
            self.no_other_current_membership(next_sprint, plan)
        if self.has_carried(sprint, plan):
            return sprint
        with self.writing():
            change = self.record_change(sprint, plan, "plan_carried", reason, {}, actor)
            if next_sprint:
                self.links.linked(Ref.build(next_sprint), Ref.build(plan), SPRINT_PLAN, actor)
                self.links.linked(Ref.build(change), Ref.build(next_sprint), CHANGE_NEXT_SPRINT, actor)
        return sprint

    def index(self, actor: Actor) -> list[dict]:
        self.owner(actor)
        return [self.summary(sprint) for sprint in self.rows()]

    def show(self, sprint_id: int, actor: Actor) -> dict:
        self.owner(actor)
        sprint = self.find(sprint_id)
        return {**self.summary(sprint), "commitments": self.commitment_data(sprint), "changes": self.change_data(sprint)}

    def summary(self, sprint: Sprint) -> dict:
        return {"id": sprint.row_id, "starts_on": sprint.starts_on, "ends_on": sprint.ends_on, "starts_at": self.utc(sprint.starts_at),
                "ends_at": self.utc(sprint.ends_at), "timezone": sprint.timezone, "length_days": sprint.length_days,
                "calendar_version": sprint.calendar_version, "state": sprint.state.value, "plan_ids": [ref.id for ref in self.links.targets(sprint, SPRINT_PLAN)]}

    def commitment_data(self, sprint: Sprint) -> list[dict]:
        rows = [self.commitments.find(ref.id) for ref in self.links.targets(sprint, SPRINT_COMMITMENT)]
        return [self.commitment(row) for row in rows]

    def commitment(self, row: SprintCommitment) -> dict:
        plan = self.links.targets(row, COMMITMENT_PLAN)[0]
        return {"id": row.row_id, "plan_id": plan.id, **row.snapshot}

    def change_data(self, sprint: Sprint) -> list[dict]:
        rows = [self.changes.find(ref.id) for ref in self.links.targets(sprint, SPRINT_CHANGE)]
        return [self.change(row) for row in rows]

    def change(self, row: SprintChange) -> dict:
        plan = self.links.targets(row, CHANGE_PLAN)
        next_sprint = self.links.targets(row, CHANGE_NEXT_SPRINT)
        return {"id": row.row_id, "change_type": row.change_type, "reason": row.reason, "data": row.data,
                "plan_id": plan[0].id if plan else None, "next_sprint_id": next_sprint[0].id if next_sprint else None,
                "created_at": row.created_at.isoformat() if row.created_at else "", "actor": row.creator.stamp if row.creator else ""}

    def plans_in(self, sprint: Sprint) -> list[Plan]:
        return [self.plans.find(ref.id) for ref in self.links.targets(sprint, SPRINT_PLAN)]

    def plan_snapshot(self, plan: Plan) -> dict:
        tasks = self.plans.plan_tasks(plan)
        return {"plan_title": plan.title, "plan_brief": plan.brief, "task_ids": [task.row_id for task in tasks],
                "tasks": [self.task_snapshot(task) for task in tasks], "due_constraint": None, "capacity_assumptions": None}

    def task_snapshot(self, task: Task) -> dict:
        domain_name = self.domains.planned_domain_name(task)
        domain = self.organization.contracts().domain(domain_name) if domain_name else None
        definition = domain.definition_of_done if domain else None
        return {"id": task.row_id, "title": task.title, "brief": task.brief, "size": None,
                "domain": domain_name, "criteria_version": definition.version if definition else None,
                "definition_of_done": definition.data() if definition else None, "depends_on": None}

    def committed_task_snapshot(self, plan: Plan, task_id: int) -> dict | None:
        periods = [self.find(ref.id) for ref in self.links.sources(plan, SPRINT_PLAN)]
        for sprint in sorted(periods, key=lambda row: row.starts_at, reverse=True):
            commitments = [self.commitments.find(ref.id) for ref in self.links.targets(sprint, SPRINT_COMMITMENT)]
            for commitment in commitments:
                task = next((row for row in commitment.snapshot.get("tasks", ()) if row.get("id") == task_id), None)
                if task is not None:
                    return task
        return None

    def record_commitment(self, sprint: Sprint, plan: Plan, actor: Actor) -> SprintCommitment:
        commitment = self.commitments.save(SprintCommitment(environment_id=sprint.environment_id, snapshot=self.plan_snapshot(plan)), actor)
        self.links.linked(Ref.build(sprint), Ref.build(commitment), SPRINT_COMMITMENT, actor)
        self.links.linked(Ref.build(commitment), Ref.build(plan), COMMITMENT_PLAN, actor)
        return commitment

    def record_change(self, sprint: Sprint, plan: Plan, kind: str, reason: str, data: dict, actor: Actor) -> SprintChange:
        change = self.changes.save(SprintChange(environment_id=sprint.environment_id, change_type=kind, reason=reason, data=data), actor)
        self.links.linked(Ref.build(sprint), Ref.build(change), SPRINT_CHANGE, actor)
        self.links.linked(Ref.build(change), Ref.build(plan), CHANGE_PLAN, actor)
        return change

    def has_plan(self, sprint: Sprint, plan: Plan) -> bool:
        return Ref.build(plan) in self.links.targets(sprint, SPRINT_PLAN)

    def no_other_current_membership(self, sprint: Sprint, plan: Plan) -> None:
        others = [self.find(ref.id) for ref in self.links.sources(plan, SPRINT_PLAN) if ref.id != sprint.row_id]
        if any(period.state != SprintState.CLOSED for period in others):
            raise Rejection(f"plan {plan.id} already has a current sprint commitment")

    def require_membership_open(self, sprint: Sprint) -> None:
        if sprint.state not in (SprintState.DRAFT, SprintState.ACTIVE):
            raise Rejection("a closed sprint cannot take plan membership")

    def has_carried(self, sprint: Sprint, plan: Plan) -> bool:
        return any(change.change_type == "plan_carried" and Ref.build(plan) in self.links.targets(change, CHANGE_PLAN)
                   for change in self.changes.numbered(ref.id for ref in self.links.targets(sprint, SPRINT_CHANGE)))

    def no_overlap(self, starts_at: float, ends_at: float, except_id: int = 0) -> None:
        overlaps = [period for period in self.rows() if period.row_id != except_id and starts_at < period.ends_at and period.starts_at < ends_at]
        if overlaps:
            raise Rejection("sprint calendar periods cannot overlap")

    def period(self, starts_on: str, timezone_name: str, length_days: int) -> tuple[float, float, str]:
        if length_days <= 0:
            raise Rejection("a sprint length must be a positive number of calendar days")
        try:
            day = date.fromisoformat(starts_on)
            zone = ZoneInfo(timezone_name)
        except (ValueError, ZoneInfoNotFoundError) as error:
            raise Rejection("a sprint needs a calendar date and an IANA timezone") from error
        end_day = day + timedelta(days=length_days)
        start = datetime.combine(day, time.min, zone)
        end = datetime.combine(end_day, time.min, zone)
        return start.timestamp(), end.timestamp(), end_day.isoformat()

    def calendar_version(self, length_days: int, timezone_name: str) -> int:
        rows = self.rows()
        if not rows:
            return 1
        latest = max(rows, key=lambda sprint: sprint.starts_at)
        return latest.calendar_version + int((latest.length_days, latest.timezone) != (length_days, timezone_name))

    def changed_calendar_version(self, sprint: Sprint, length_days: int, timezone_name: str) -> int:
        return sprint.calendar_version + int((sprint.length_days, sprint.timezone) != (length_days, timezone_name))

    @staticmethod
    def utc(moment: float) -> str:
        return datetime.fromtimestamp(moment, timezone.utc).isoformat()

    @staticmethod
    def owner(actor: Actor) -> None:
        if not actor.is_desk_user() or actor.number() != LOCAL_USER:
            raise Rejection("only the organization owner may change or read sprint commitments")
