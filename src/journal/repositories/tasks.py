from collections.abc import Sequence
from datetime import datetime, timezone

from journal.db.connection import Connection
from journal.db.query import Query
from journal.events.bus import Bus
from journal.models.agent import Agent
from journal.models.check import Check
from journal.models.link import Link
from journal.models.model import Model
from journal.models.plan import Plan
from journal.models.question import Question
from journal.models.support.ref import Ref
from journal.models.task import Task
from journal.models.task_state import TaskState
from journal.models.plan_state import PlanState
from journal.support.actor import Actor
from journal.support.rejection import Rejection
from journal.repositories.checks import Checks
from journal.repositories.links import Links
from journal.repositories.questions import Questions
from journal.repositories.scope import Scope
from journal.repositories.scoped_repository import ScopedRepository

WAIT_LINK = "waits_on"
CURRENT_TASK_LINK = "in_hand"
WORKED_LINK = "worked_on"
QUEUED_LINK = "queued_for"
WORKERS = "workers"
WORKER_TASK = "task {task} is not worker {worker}'s: a worker works on the task it holds, {holdings}"
HOLDER_REFUSAL = "task {task} is held by worker {worker} until its work is merged or released: send that worker its next job, or release it first"
PLAN_LINK = "in_plan"
USER_PREFIX = "user:"
CLOSED = (TaskState.FINISHED, TaskState.CANCELLED)


UNAPPROVED_PLAN_STATES = tuple(state.value for state in PlanState if state.is_unapproved())

CLOSED_STATES = (TaskState.FINISHED, TaskState.CANCELLED)

class Tasks(ScopedRepository[Task]):
    model = Task
    member_links = (PLAN_LINK,)

    def __init__(self, connection: Connection, bus: Bus, scope: Scope, links: Links, questions: Questions, checks: Checks) -> None:
        super().__init__(connection, bus, scope)
        self.links, self.checks = links, checks
        self.awaitable: dict[str, Tasks | Questions | Checks] = {Task.table(): self, Question.table(): questions, Check.table(): checks}

    def open_waits(self, row: Task | Plan) -> list[Ref]:
        return [ref for ref in self.links.targets(row, WAIT_LINK) if not self.waiting(ref).is_resolved()]

    def waits_reach(self, start: Ref, goal: Ref) -> bool:
        viewed, todo = set(), [start]
        while todo:
            ref = todo.pop()
            if ref == goal:
                return True
            if ref in viewed or ref.type != Task.table():
                continue
            viewed.add(ref)
            todo += self.links.targets(self.find(ref.id), WAIT_LINK)
        return False

    def waiting(self, ref: Ref) -> Task | Question | Check:
        return self.awaitable[ref.type].find(ref.id)

    def waiting_ids(self, tasks: list[Task]) -> set[int]:
        return set(self.open_wait_refs(tasks))

    def open_wait_refs(self, tasks: list[Task]) -> dict[int, list[Ref]]:
        waits: dict[int, list[Ref]] = {}
        for link in self.links.model_links("source", tasks, WAIT_LINK):
            if not self.waiting(link.target).is_resolved():
                waits.setdefault(link.source.id, []).append(link.target)
        return waits

    def blocked_without_wait(self) -> list[Task]:
        return [task for task in self.with_state(TaskState.BLOCKED) if not self.open_waits(task)]

    def broken_waits(self) -> list[tuple[Task, Check]]:
        return [(task, check) for check in self.checks.broken_waits() for task in self.waiting_refs(check)]

    def waiting_refs(self, model) -> list[Task]:
        return [task for ref in self.links.sources(model, WAIT_LINK) if ref.type == Task.table() and (task := self.find(ref.id)).state in (TaskState.BLOCKED, TaskState.PAUSED)]

    def reason(self, row: Task | Plan) -> str:
        matched = [f"{ref.type[:-1]} {ref.id}" for ref in self.links.targets(row, WAIT_LINK)]
        return ", ".join(part for part in (*matched, row.waiting_reason()) if part)

    def unclosed_tasks(self) -> list[Task]:
        return self.selected(self.unclosed_query().order_descending("priority").order("id"))

    def unclosed_page(self, rows: int) -> list[Task]:
        return self.selected(self.unclosed_query().order_descending("priority").order("id").limit(rows))

    def unclosed_count(self) -> int:
        return self.counted(self.unclosed_query())

    def closed_count(self) -> int:
        return self.counted(self.query().filter_listed("state", list(CLOSED_STATES)))

    def unclosed_query(self) -> Query:
        return self.query().filter_unlisted("state", list(CLOSED_STATES))

    def unfinished_ids(self, numbers: list[int]) -> list[int]:
        return [number for number in numbers if self.matching(id=number, state=TaskState.OPEN) or self.matching(id=number, state=TaskState.STARTED) or self.matching(id=number, state=TaskState.DELEGATED)]

    def ready_waiting_tasks(self, model) -> list[Task]:
        return [task for task in self.waiting_refs(model) if not self.open_waits(task)]

    def other_started_tasks(self, current: Task | None) -> list[Task]:
        return [task for task in self.with_state(TaskState.STARTED) if current is None or task.id != current.id]

    def numbered_anywhere(self, ids: list[int]) -> list[Task]:
        return self.selected_globally(self.query().filter_listed("id", ids).order("id")) if ids else []

    def open_tasks(self) -> list[Task]:
        return self.actionable(TaskState.OPEN)

    def blocked_tasks(self) -> list[Task]:
        return self.actionable(TaskState.BLOCKED)

    def paused_tasks(self) -> list[Task]:
        return self.free_tasks(TaskState.PAUSED, (PlanState.PAUSED.value,))

    def actionable(self, state: TaskState) -> list[Task]:
        return self.free_tasks(state, UNAPPROVED_PLAN_STATES)

    def free_tasks(self, state: TaskState, plan_states: tuple[str, ...]) -> list[Task]:
        return self.selected(self.free_query(state, plan_states))

    def open_page_ids(self, rows: int) -> list[int]:
        return self.selected_ids(self.free_query(TaskState.OPEN, UNAPPROVED_PLAN_STATES).limit(rows))

    def open_count(self) -> int:
        return self.counted(self.free_query(TaskState.OPEN, UNAPPROVED_PLAN_STATES))

    def has_stale_open(self, moment: datetime) -> bool:
        return self.counted(self.free_query(TaskState.OPEN, UNAPPROVED_PLAN_STATES).filter_less_equal("updated_at", moment)) > 0

    def free_query(self, state: TaskState, plan_states: tuple[str, ...]) -> Query:
        plans = Query.build(Plan).filter_listed("state", list(plan_states)).filter_named(self.links.query(), "target")
        planned = self.links.query().filter(kind=PLAN_LINK).filter_ref("source", self.query()).filter_existing(plans)
        return self.query().filter(state=state).filter_absent(planned).order_descending("priority").order("id")

    def recent_completions(self, start: datetime, end: datetime) -> list[Task]:
        return self.selected(self.query().filter(state=TaskState.FINISHED).filter_greater_equal("finished_at", start).filter_less("finished_at", end).order("id"))

    def with_state(self, state: TaskState) -> list[Task]:
        return self.matching(state=state)

    def current(self, agent: Agent) -> Task | None:
        return self.holder_task(Ref.build(agent))

    def is_driven(self, task: Task) -> bool:
        return Ref.build(task) in self.scope.bound()

    def holder_task(self, holder: Ref) -> Task | None:
        held = self.links.query().filter(source=holder, kind=CURRENT_TASK_LINK).filter_ref("target", self.query())
        tasks = self.selected(self.query().filter_listed("state", [TaskState.STARTED, TaskState.DELEGATED]).filter_existing(held).order("id"))
        return next((task for task in tasks if task.state == TaskState.STARTED), tasks[0] if tasks else None)

    def holder_task_ids(self, holder: Ref) -> tuple[int, ...]:
        return tuple(link.target.id for link in self.links.all_matching(source=holder, kind=CURRENT_TASK_LINK))

    def last_task_id(self, holder: Ref) -> int:
        task_ids = self.recent_task_ids(holder, 1)
        return task_ids[-1] if task_ids else 0

    def recent_task_ids(self, holder: Ref, count: int) -> tuple[int, ...]:
        links = self.links.selected(self.links.query().filter(source=holder, kind=CURRENT_TASK_LINK).order_descending("id").limit(count))
        return tuple(reversed([link.target.id for link in links]))

    def holder(self, task: Task) -> Ref | None:
        holders = self.links.sources(task, CURRENT_TASK_LINK)
        return holders[-1] if holders else None

    def agent_held(self, state: TaskState, agents: Query) -> list[Task]:
        held = self.links.query().filter(kind=CURRENT_TASK_LINK).filter_ref("target", self.query()).filter_existing(agents.filter_named(self.links.query(), "source"))
        return self.selected(self.query().filter(state=state).filter_existing(held).order("id"))

    def row_holders(self, rows: list[Task]) -> dict[int, Ref]:
        return {link.target.id: link.source for link in self.links.model_links("target", rows, CURRENT_TASK_LINK)}

    def holder_started(self, started: Task, holder: Ref | None, actor: Actor) -> Task:
        self.assign_holder(started, holder, actor)
        return self.save(started, actor)

    def assign_holder(self, started: Task, holder: Ref | None, actor: Actor) -> None:
        if holder is None:
            return
        counterpart = self.holder_task(holder)
        if counterpart is not None and counterpart.id != started.id:
            raise Rejection(f"task {counterpart.id} is in hand: finish it, or pause it with `journal task pause {counterpart.id} \"<why>\"`, before task {started.id} is started")
        self.handover(started, holder, actor)

    def guard_worker_task(self, task: Task, holder: Ref | None, actor: Actor) -> None:
        owner = self.holder(task)
        if owner is not None and owner != holder and owner.type == WORKERS and not actor.is_user():
            raise Rejection(HOLDER_REFUSAL.format(task=task.id, worker=owner.id))

    def handover(self, task: Task, holder: Ref, actor: Actor) -> None:
        self.guard_worker_task(task, holder, actor)
        owner = self.holder(task)
        target = Ref.build(task)
        for link in self.links.all_matching(target=target, kind=CURRENT_TASK_LINK):
            if link.source != holder:
                self.links.delete(link, actor)
        if owner != holder:
            self.links.save(Link(source=holder, target=target, kind=CURRENT_TASK_LINK), actor)
        if holder.type == WORKERS and not self.links.all_matching(source=holder, target=target, kind=WORKED_LINK):
            self.links.save(Link(source=holder, target=target, kind=WORKED_LINK), actor)
        if holder.type == WORKERS and task.state != TaskState.DELEGATED:
            self.save(task.delegated(datetime.now(timezone.utc)), actor)
        for link in self.links.all_matching(source=holder, target=target, kind=QUEUED_LINK):
            self.links.delete(link, actor)

    def queued(self, task: Task, worker: Ref, actor: Actor) -> Task:
        if not self.is_free(task):
            raise Rejection(f"task {task.id} is {task.state}: only an open task, or a started or paused one in your own hands, waits in a worker's queue")
        if not self.links.all_matching(source=worker, target=Ref.build(task), kind=QUEUED_LINK):
            self.links.save(Link(source=worker, target=Ref.build(task), kind=QUEUED_LINK), actor)
        return self.save(task.delegated(datetime.now(timezone.utc)), actor)

    def queued_first(self, task: Task, worker: Ref, actor: Actor) -> Task:
        waiting_for = self.links.all_matching(target=Ref.build(task), kind=QUEUED_LINK)
        if not self.is_free(task) and not (task.state == TaskState.DELEGATED and waiting_for):
            raise Rejection(f"task {task.id} is {task.state}: only an open task, a started or paused one in your own hands, or one waiting in a worker's queue, goes first in a worker's queue")
        for link in waiting_for:
            self.links.delete(link, actor)
        others = [waiting for waiting in self.queue(worker) if waiting.id != task.id]
        for link in self.links.all_matching(source=worker, kind=QUEUED_LINK):
            self.links.delete(link, actor)
        for waiting in (task, *others):
            self.links.save(Link(source=worker, target=Ref.build(waiting), kind=QUEUED_LINK), actor)
        return task if task.state == TaskState.DELEGATED else self.save(task.delegated(datetime.now(timezone.utc)), actor)

    def let_go(self, task: Task, holder: Ref | None, actor: Actor) -> None:
        if holder is None or holder.type == WORKERS or task.state not in (TaskState.STARTED, TaskState.PAUSED):
            return
        for link in self.links.all_matching(source=holder, target=Ref.build(task), kind=CURRENT_TASK_LINK):
            self.links.delete(link, actor)

    def is_free(self, task: Task) -> bool:
        return task.state == TaskState.OPEN or (task.state in (TaskState.STARTED, TaskState.PAUSED) and self.holder(task) is None)

    def queue(self, worker: Ref) -> list[Task]:
        links = sorted(self.links.all_matching(source=worker, kind=QUEUED_LINK), key=lambda link: link.row_id)
        return [self.find(n) for n in dict.fromkeys(link.target.id for link in links)]

    def worker_task(self, task_id: int, worker: int) -> Task:
        holdings = self.holder_task_ids(Ref(WORKERS, worker))
        if task_id not in holdings:
            raise Rejection(WORKER_TASK.format(task=task_id, worker=worker, holdings=", ".join(f"task {n}" for n in holdings) or "no task"))
        return self.find(task_id)

    def release(self, holder: Ref, actor: Actor) -> None:
        self.freed(holder, CURRENT_TASK_LINK, actor)

    def release_task(self, holder: Ref, task_id: int, actor: Actor) -> None:
        for link in self.links.all_matching(source=holder, target=Ref("tasks", task_id), kind=CURRENT_TASK_LINK):
            self.links.delete(link, actor)

    def unqueued(self, holder: Ref, actor: Actor) -> None:
        self.freed(holder, QUEUED_LINK, actor)

    def freed(self, holder: Ref, kind: str, actor: Actor) -> None:
        for link in self.links.all_matching(source=holder, kind=kind):
            self.links.delete(link, actor)
            for task in self.matching(id=link.target.id, state=TaskState.DELEGATED):
                self.save(task.released(datetime.now(timezone.utc).timestamp()), actor)

    def block_batch(self, start_at: float) -> list[Task]:
        return [task for task in self.with_state(TaskState.BLOCKED) if task.updated_at is not None and task.updated_at.timestamp() >= start_at]

    def has_worker_holder(self, task_ids: Sequence[int]) -> bool:
        return self.links.ref_count("target", [Ref(Task.table(), task_id) for task_id in task_ids], CURRENT_TASK_LINK, WORKERS) > 0

    def task_worker_holdings(self, task_ids: set[int]) -> dict[int, int]:
        refs = [Ref(Task.table(), task_id) for task_id in sorted(task_ids)]
        return {link.target.id: link.source.id for link in self.links.ref_links("target", refs, CURRENT_TASK_LINK) if link.source.type == WORKERS}

    def workers_of(self, task_ids: set[int]) -> set[int]:
        refs = [Ref(Task.table(), task_id) for task_id in sorted(task_ids)]
        queued = {link.source.id for link in self.links.ref_links("target", refs, QUEUED_LINK) if link.source.type == WORKERS}
        return {*self.task_worker_holdings(task_ids).values(), *queued}

    def worker_task_holdings(self, workers: list[Model]) -> dict[int, int]:
        return {link.target.id: link.source.id for link in self.links.model_links("source", workers, CURRENT_TASK_LINK)}

    def worker_holdings(self) -> dict[int, int]:
        return {link.target.id: link.source.id for link in self.links.selected(self.links.query().filter(kind=CURRENT_TASK_LINK).filter_prefix("source", f"{WORKERS}:").order("id"))}

    # the task each of the workers worked on before the one it holds, read from their own links alone
    def earlier_tasks(self, workers: list[Model], holdings: dict[int, int]) -> dict[int, int]:
        worker_tasks = {worker: task for task, worker in holdings.items()}
        return {link.source.id: link.target.id for link in self.links.model_links("source", workers, WORKED_LINK) if worker_tasks.get(link.source.id) != link.target.id}

    # the tasks queued for each of the workers, in the order they were queued
    def queues(self, workers: list[Model]) -> dict[int, list[Task]]:
        links = self.links.model_links("source", workers, QUEUED_LINK)
        tasks = {task.row_id: task for task in self.numbered({link.target.id for link in links})}
        queued: dict[int, list[Task]] = {}
        for link in links:
            if link.target.id in tasks and tasks[link.target.id] not in queued.setdefault(link.source.id, []):
                queued[link.source.id].append(tasks[link.target.id])
        return queued

    def previous_creation(self, task: Task) -> datetime:
        previous = self.selected(self.query().filter_less("id", task.id).order_descending("id").limit(1))
        return previous[0].created_at if previous else datetime.min.replace(tzinfo=timezone.utc)

    def unfinished_count(self) -> int:
        planned = self.links.query().filter(kind=PLAN_LINK).filter_ref("source", self.query())
        return self.counted(self.query().filter_unlisted("state", CLOSED).filter_absent(planned))

    def unviewed(self) -> int:
        return self.counted(self.query().filter_unlisted("state", CLOSED).filter_missing_prefix("creator", USER_PREFIX))
