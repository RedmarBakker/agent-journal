from datetime import datetime, timezone
from journal.db.connection import Connection
from journal.db.query import Query
from journal.events.bus import Bus
from journal.support.actor import Actor
from journal.models.link import Link
from journal.models.phase import Phase
from journal.models.plan import Plan
from journal.models.plan_state import PlanState
from journal.support.rejection import Rejection
from journal.models.task import Task
from journal.models.task_state import TaskState
from journal.repositories.links import Links
from journal.repositories.phases import PHASE_TASK_LINK, Phases
from journal.repositories.scope import Scope
from journal.repositories.scoped_repository import ScopedRepository
from journal.repositories.tasks import CLOSED_STATES, CURRENT_TASK_LINK, PLAN_LINK, WAIT_LINK, WORKERS, Tasks
from journal.repositories.workers import Workers
from journal.models.phase_states import PhaseStates
from journal.models.support.ref import Ref
from journal.support.time_source import TimeSource


PHASE_LINK = "in_phase"
# the most tasks of one plan on offer at once
QUEUED_TASKS = 10


class Plans(ScopedRepository[Plan]):
    """The plans and their rows: tasks and phases in the order they were added, the plan's questions answered over them, and its writes: approve, start (a finished plan is done, else its postponed or next task is taken in hand, one at a time, else it waits for a task to open), postpone (its task in hand postponed first, so the plan's event comes last), cancel (with the tasks that are its alone)."""

    model = Plan

    def __init__(self, connection: Connection, bus: Bus, scope: Scope, links: Links, tasks: Tasks, phases: Phases, workers: Workers, time_source: TimeSource) -> None:
        super().__init__(connection, bus, scope, time_source)
        self.links, self.tasks, self.phases, self.workers = links, tasks, phases, workers

    def approve(self, plan: Plan, actor: Actor) -> Plan:
        if plan.state == PlanState.REVIEWING:
            raise Rejection(f"plan {plan.id} is in review: it can be approved once its reviewers are back and their findings are in it")
        if plan.state in (PlanState.STARTED, PlanState.FINISHED, PlanState.CANCELLED):
            return plan
        return self.save(plan.approved(self._time().timestamp(), actor.is_user()), actor)

    def cancel(self, plan: Plan, actor: Actor) -> list[Task]:
        self.save(plan.cancelled(self.time_source.moment().timestamp(), actor.is_user()), actor)
        cancelled = []
        for task in self.plan_tasks(plan):
            if task.is_closed() or self.is_shared(task, plan):
                continue
            cancelled.append(self.tasks.save(task.cancelled(self.time_source.moment(), f"its plan {plan.id} was cancelled"), actor))
        return cancelled

    def is_shared(self, task: Task, plan: Plan) -> bool:
        return any(ref.id != plan.id and self.find(ref.id).state != PlanState.CANCELLED for ref in self.links.targets(task, PLAN_LINK))

    def plan_states(self, task: Task) -> set[PlanState]:
        return {plan.state for plan in self.containing(task)}

    def containing(self, task: Task) -> list[Plan]:
        return [plan for ref in self.links.targets(task, PLAN_LINK) if (plan := self.find(ref.id)).state in (PlanState.APPROVED, PlanState.STARTED, PlanState.PAUSED, PlanState.BLOCKED)]

    def waiting_plans(self, model) -> list[Plan]:
        return [plan for ref in self.links.sources(model, WAIT_LINK) if ref.type == Plan.table() and (plan := self.find(ref.id)).is_blocked()]

    def is_stalled(self, plan: Plan) -> bool:
        return plan.is_stalled(self.remaining_count(plan), self.tasks.counted(self.plan_task_query(plan).filter(state=TaskState.BLOCKED)))

    def remaining_count(self, plan: Plan) -> int:
        return self.tasks.counted(self.plan_task_query(plan).filter_unlisted("state", list(CLOSED_STATES)))

    def plan_task_query(self, plan: Plan) -> Query:
        planned = self.links.query().filter(kind=PLAN_LINK, target=Ref.build(plan)).filter_ref("source", self.tasks.query())
        return self.tasks.query().filter_existing(planned)

    def task_count(self, plan: Plan) -> int:
        return self.tasks.counted(self.plan_task_query(plan))

    # the work open for workers: the open tasks of the approved and started plans, neither blocked, paused, delegated, queued nor in hand
    def open_work_count(self) -> int:
        return sum(self.unassigned_count(plan) for plan in (*self.approved(), *self.running_plans()))

    def unassigned_count(self, plan: Plan) -> int:
        return self.tasks.counted(self.plan_task_query(plan).filter(state=TaskState.OPEN, delegated=False))

    def blocked_count(self, plan: Plan) -> int:
        return self.tasks.counted(self.plan_task_query(plan).filter(state=TaskState.BLOCKED))

    def last_moved(self, plan: Plan) -> float:
        latest = self.tasks.selected(self.plan_task_query(plan).order_descending("updated_at").limit(1))
        return max(plan.updated_at, *(task.updated_at for task in latest)).timestamp()

    def plan_tasks(self, plan: Plan) -> list[Task]:
        return self.tasks.numbered(ref.id for ref in self.links.sources(plan, PLAN_LINK))

    def unphased_task_ids(self, plan: Plan, phased_ids: list[int]) -> list[int]:
        return [ref.id for ref in self.links.sources_except(plan, PLAN_LINK, [Ref(Task.table(), task_id) for task_id in phased_ids])]

    def recent_task_ids(self, plan: Plan, count: int) -> list[int]:
        return self.tasks.selected_ids(self.plan_task_query(plan).order_descending("updated_at").order_descending("id").limit(count))

    def plan_task_ids(self, plan: Plan) -> list[int]:
        return [ref.id for ref in self.links.sources(plan, PLAN_LINK)]

    def phase_links(self, phases: list[Phase]) -> list[Link]:
        return self.links.model_links("target", phases, PHASE_LINK)

    def plan_phases(self, plan: Plan) -> list[Phase]:
        return self.phases.selected(self.plan_phase_query(plan).order("id"))

    def plan_phase_query(self, plan: Plan) -> Query:
        linked = self.links.query().filter(target=Ref.build(plan), kind=PHASE_TASK_LINK).filter_ref("source", self.phases.query())
        return self.phases.query().filter_existing(linked)

    def phase_counts(self, plans: list[Plan]) -> dict[int, int]:
        return self.links.target_counts(plans, PHASE_TASK_LINK)

    def task_counts(self, plans: list[Plan]) -> dict[int, int]:
        return self.links.target_counts(plans, PLAN_LINK)

    def phase_tasks(self, phase: Phase) -> list[Task]:
        return self.tasks.numbered(ref.id for ref in self.links.sources(phase, PHASE_LINK))

    def phase_states(self, plan: Plan) -> list[PhaseStates]:
        return [PhaseStates(number, phase, self.phase_state_counts(phase)) for number, phase in enumerate(self.plan_phases(plan), 1)]

    def phase_state_counts(self, phase: Phase) -> dict[TaskState, int]:
        members = self.links.query().filter(kind=PHASE_LINK, target=Ref.build(phase)).filter_ref("source", self.tasks.query())
        return {TaskState(state): count for state, count in self.tasks.grouped_counts(self.tasks.query().filter_existing(members), "state").items()}

    def phase_task_ids(self, phases: list[Phase]) -> dict[int, list[int]]:
        members: dict[int, list[int]] = {phase.id: [] for phase in phases}
        for link in self.phase_links(phases):
            members[link.target.id].append(link.source.id)
        return members

    def reviewing(self) -> list[Plan]:
        return self.matching(state=PlanState.REVIEWING)

    def reviewed(self) -> list[Plan]:
        return self.selected(self.query().filter(state=PlanState.REVIEWING, reviewers=0).order("id"))

    def approved(self) -> list[Plan]:
        return self.matching(state=PlanState.APPROVED)

    def related(self) -> list[Task]:
        started = [plan for plan in self.scoped() if plan.state == PlanState.STARTED]
        if not started:
            return self.free()
        task = self.next_task(started[0])
        return [task] if task else []

    def stalled_plans(self, task: Task) -> list[Plan]:
        return [plan for plan in self.started_plans(task) if self.is_stalled(plan)]

    def complete_plans(self) -> list[Plan]:
        return [plan for plan in self.all() if plan.state == PlanState.STARTED and self.finished(plan)]

    def running_plans(self) -> list[Plan]:
        return self.matching(state=PlanState.STARTED)

    def running_plans_beside(self, plan_id: int) -> list[Plan]:
        return self.selected(self.query().filter(state=PlanState.STARTED).filter_unequal("id", plan_id))

    def finished_plans(self, task: Task) -> list[Plan]:
        return [plan for plan in self.containing(task) if self.finished(plan)]

    def loose_tasks(self, plan: Plan) -> list[Task]:
        phased = {task.id for phase in self.plan_phases(plan) for task in self.phase_tasks(phase)}
        return [task for task in self.plan_tasks(plan) if task.id not in phased]

    def started_plans(self, task: Task) -> list[Plan]:
        return [plan for plan in self.containing(task) if plan.state == PlanState.STARTED]

    def unstarted_plans(self, task: Task) -> list[Plan]:
        return [plan for plan in self.containing(task) if plan.state in (PlanState.APPROVED, PlanState.PAUSED)]

    def resume_plan(self, plan: Plan, task: Task, actor: Actor) -> Plan:
        return self.save(plan.started(task, self.time_source.moment().timestamp()), actor)

    def unapproved(self, task: Task) -> list[Plan]:
        return [plan for ref in self.links.targets(task, PLAN_LINK) if (plan := self.find(ref.id)).state.is_unapproved()]

    def free(self) -> list[Task]:
        open_tasks = self.tasks.open_tasks()
        planned = {link.source.id for link in self.links.model_links("source", open_tasks, PLAN_LINK)}
        delegated = set(self.workers.containing({t.row_id for t in open_tasks}))
        return [t for t in open_tasks if t.id not in planned and t.id not in delegated]

    def finished(self, plan: Plan) -> bool:
        return plan.is_finished(self.tasks.counted(self.plan_task_query(plan)), self.remaining_count(plan))

    def resumable(self, plan: Plan) -> Task | None:
        return self.first_task(plan, TaskState.PAUSED, self.tasks.query()) or self.next_task(plan)

    def started_task(self, plan: Plan) -> Task | None:
        started = self.tasks.selected(self.plan_task_query(plan).filter(state=TaskState.STARTED, delegated=False).order("id").limit(1))
        return started[0] if started else None

    def next_task(self, plan: Plan) -> Task | None:
        return self.first_task(plan, TaskState.OPEN, self.startable_tasks(plan))

    def startable_tasks(self, plan: Plan) -> Query:
        return self.tasks.query().filter(state=TaskState.OPEN, delegated=False).filter_unlisted("id", sorted(self.waiting_task_ids(plan))).filter_absent(self.worker_holdings())

    def queued_tasks(self, plan: Plan) -> list[Task]:
        queued: list[Task] = []
        while len(queued) < QUEUED_TASKS and (task := self.first_task(plan, TaskState.OPEN, self.startable_tasks(plan).filter_unlisted("id", [queued_task.row_id for queued_task in queued]))) is not None:
            queued.append(task)
        return queued

    # the order a plan's work is taken up in: a paused task whose waits are over first, then the next open one; a blocked task, or a paused
    # one still waiting, never stops the plan
    def following_task(self, plan: Plan) -> Task | None:
        paused = self.first_task(plan, TaskState.PAUSED, self.tasks.query().filter_unlisted("id", sorted(self.waiting_task_ids(plan))))
        return paused if paused is not None else self.next_task(plan)

    # the plan's first task in its order that is in the state and matches the candidates: its phases' tasks phase by phase, each in the order
    # it joined its phase, then its tasks under no phase in the order they joined the plan; the first phase holding one is found in one read
    def first_task(self, plan: Plan, state: TaskState, candidates: Query) -> Task | None:
        matching = candidates.filter(state=state)
        phase_links = self.links.query().filter(kind=PHASE_LINK)
        task_links = phase_links.filter_ref("target", self.phases.query()).filter_existing(matching.filter_named(phase_links, "source"))
        first_phase = self.phases.selected(self.plan_phase_query(plan).filter_existing(task_links).order("id").limit(1))
        if first_phase:
            return self.first_link(phase_links.filter(target=Ref.build(first_phase[0])), matching)
        planned = phase_links.filter_existing(self.plan_phase_query(plan).filter_named(phase_links, "target"))
        unphased = matching.filter_absent(planned.filter_ref("source", self.tasks.query()))
        return self.first_link(self.links.query().filter(kind=PLAN_LINK, target=Ref.build(plan)), unphased)

    def has_resumable(self, plan: Plan) -> bool:
        plan_links = self.links.query().filter(kind=PLAN_LINK, target=Ref.build(plan))
        return self.has_link(plan_links, self.tasks.query().filter(state=TaskState.PAUSED)) or self.has_link(plan_links, self.startable_tasks(plan))

    def has_link(self, links: Query, tasks: Query) -> bool:
        return bool(self.links.selected(links.filter_existing(tasks.filter_named(links, "source")).limit(1)))

    def first_link(self, links: Query, tasks: Query) -> Task | None:
        first = self.links.selected(links.filter_existing(tasks.filter_named(links, "source")).order("id").limit(1))
        return self.tasks.find(first[0].source.id) if first else None

    def waiting_task_ids(self, plan: Plan) -> set[int]:
        waits = self.links.query().filter(kind=WAIT_LINK)
        return self.tasks.waiting_ids(self.tasks.selected(self.plan_task_query(plan).filter_existing(waits.filter_ref("source", self.tasks.query()))))

    def worker_holdings(self) -> Query:
        return self.links.query().filter(kind=CURRENT_TASK_LINK).filter_prefix("source", f"{WORKERS}:").filter_ref("target", self.tasks.query())

    def checkpoint_plans(self, plan: Plan) -> PhaseStates | None:
        return plan.checkpoint_phase(self.phase_states(plan))

    def ended_phase(self, plan: Plan) -> PhaseStates | None:
        return plan.ended_phase(self.phase_states(plan))

    def phase_end_time(self, phase: Phase) -> float:
        return max(((task.completed_at or task.update_time).timestamp() for task in self.phase_tasks(phase)), default=0.0)

    def start(self, plan: Plan, holder: Ref | None, actor: Actor) -> Plan:
        time = self.time_source.moment()
        task = self.resumable(plan)
        if task is None or self.is_complete(plan):
            return self.opened(plan, actor)
        following = task.plan_started(time, plan.row_id)
        self.tasks.assign_holder(following, holder, actor)
        started = self.save(plan.started(task, time.timestamp()), actor)
        self.tasks.save(following, actor)
        return started

    def opened(self, plan: Plan, actor: Actor) -> Plan:
        time = self.time_source.moment().timestamp()
        return self.save(plan.finished(time) if self.is_complete(plan) else plan.started_without_task(time), actor)

    def is_complete(self, plan: Plan) -> bool:
        return plan.startable().is_finished(self.tasks.counted(self.plan_task_query(plan)), self.remaining_count(plan))

    def postpone(self, plan: Plan, actor: Actor) -> Plan:
        time = self.time_source.moment()
        postponed = self.save(plan.postponed(time.timestamp(), actor.is_user()), actor)
        for task in self.tasks.selected(self.plan_task_query(plan).filter(state=TaskState.STARTED).order("id")):
            self.tasks.save(task.paused(f"plan {plan.id} was paused", time), actor)
        return postponed
