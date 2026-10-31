from collections.abc import Sequence
from dataclasses import replace
from datetime import datetime, timezone

from journal.db.connection import Connection
from journal.db.query import Query
from journal.features.estimates.estimates_options import EstimatesOptions, wip_limit
from journal.events.bus import Bus
from journal.events.rows.released_tasks import ReleasedTasks
from journal.events.rows.task_started import TaskStarted
from journal.models.agent import Agent
from journal.models.check import Check
from journal.models.link import Link
from journal.models.model import Model
from journal.models.plan import Plan, USER_PAUSER
from journal.models.question import Question
from journal.models.support.ref import Ref
from journal.models.task import Task
from journal.support.task_priority import NORMAL
from journal.models.task_state import TaskState
from journal.models.plan_state import PlanState
from journal.support.actor import Actor
from journal.support.rejection import Rejection
from journal.support.missing_row import MissingRow
from journal.repositories.checks import Checks
from journal.repositories.links import Links
from journal.repositories.questions import Questions
from journal.repositories.scope import Scope
from journal.repositories.agents import Agents
from journal.repositories.repository import PAGE_ROWS
from journal.repositories.rows import Rows
from journal.repositories.setting_rows import SettingRows
from journal.repositories.scoped_repository import ScopedRepository
from journal.support.time_source import TimeSource

WAIT_LINK = "waits_on"
DEPENDENCY_LINK = "depends_on"
DELIVERY_GATE_LINK = "delivery_gate_for"
# a task waiting in testing links to the run that tests it
TEST_LINK = "tested_by"
CURRENT_TASK_LINK = "in_hand"
WORKED_LINK = "worked_on"
QUEUED_LINK = "queued_for"
FINISHED_LINK = "finished_unmerged"
WORKERS = "workers"
WORKER_TASK = "task {task} is not worker {worker}'s: a worker works on the task it holds, {holdings}"
PLAN_LINK = "in_plan"
USER_PREFIX = "user:"
AGENT_CREATOR = "agent:"
CLOSED = (TaskState.COMPLETED, TaskState.CANCELLED)


UNAPPROVED_PLAN_STATES = tuple(state.value for state in PlanState if state.is_unapproved())

CLOSED_STATES = (TaskState.COMPLETED, TaskState.CANCELLED)

class Tasks(ScopedRepository[Task]):
    """A completed task sent back short is the one in hand again, and the task the worker reported on waits for the merge in its place; the tasks a worker held before the one it holds, every task it ever held, those it completed and those queued for it are read from their own links alone, in the order it took them."""

    model = Task

    def __init__(self, connection: Connection, bus: Bus, scope: Scope, links: Links, questions: Questions,
                 checks: Checks, time_source: TimeSource, rows: Rows, agents: Agents, settings: SettingRows) -> None:
        super().__init__(connection, bus, scope, time_source)
        self.row_reader = rows
        self.links, self.checks, self.agents, self.settings = links, checks, agents, settings
        self.awaitable: dict[str, Tasks | Questions | Checks] = {Task.table(): self, Question.table(): questions, Check.table(): checks}

    def open_waits(self, row: Task | Plan) -> list[Ref]:
        return [ref for ref in self.links.targets(row, WAIT_LINK) if not self.is_wait_resolved(ref)]

    def work_reaches(self, start: Ref, goal: Ref) -> bool:
        viewed, todo = set(), [start]
        while todo:
            ref = todo.pop()
            if ref == goal:
                return True
            if ref in viewed:
                continue
            viewed.add(ref)
            if ref.type == Task.table():
                task = self.find(ref.id)
                todo += self.links.targets(task, WAIT_LINK)
                todo += self.links.targets(task, DEPENDENCY_LINK)
                todo += self.links.targets(task, DELIVERY_GATE_LINK)
            if ref.type == Plan.table():
                todo += [link.target for link in self.links.ref_links("source", [ref], WAIT_LINK)]
                todo += self.links.ref_sources(ref, PLAN_LINK)
        return False

    def require_acyclic_link(self, link: Link) -> None:
        if link.link_type in (WAIT_LINK, DEPENDENCY_LINK, DELIVERY_GATE_LINK) and self.work_reaches(link.target, link.source):
            raise Rejection(f"{link.source} waiting on {link.target} would close a cycle that nothing could ever end")

    def dependency_gaps(self, tasks: Sequence[Task]) -> dict[int, tuple[Ref, ...]]:
        if not tasks:
            return {}
        unstarted = {task.row_id for task in tasks if task.started_at is None}
        links = [link for link in self.links.model_links("source", tasks, DEPENDENCY_LINK) if link.source.id in unstarted]
        if not links:
            return {}
        targets = {row.row_id: row for row in self.numbered(link.target.id for link in links if link.target.type == Task.table())}
        gaps: dict[int, list[Ref]] = {}
        for link in links:
            if link.target.type != Task.table() or link.target.id not in targets or targets[link.target.id].state != TaskState.COMPLETED:
                gaps.setdefault(link.source.id, []).append(link.target)
        return {task_id: tuple(refs) for task_id, refs in gaps.items()}

    def unmet_prerequisites(self, task: Task) -> list[Ref]:
        return list(self.dependency_gaps([task]).get(task.row_id, ()))

    def unmet_dependency_ids(self, tasks: Sequence[Task]) -> set[int]:
        return set(self.dependency_gaps(tasks))

    def unavailable_task_ids(self, tasks: Sequence[Task]) -> set[int]:
        return self.unmet_dependency_ids(tasks) | self.waiting_ids(list(tasks))

    def unavailable_task_ids_for_ids(self, task_ids: list[int]) -> set[int]:
        refs = [Ref(Task.table(), task_id) for task_id in task_ids]
        if not self.links.ref_links("source", refs, DEPENDENCY_LINK) and not self.links.ref_links("source", refs, WAIT_LINK):
            return set()
        return self.unavailable_task_ids(self.numbered(task_ids))

    def require_prerequisites(self, task: Task) -> None:
        unmet = self.unmet_prerequisites(task)
        if unmet:
            waiting = ", ".join(f"task {ref.id}" for ref in unmet)
            raise Rejection(f"task {task.id} is unavailable until planned prerequisite {waiting} is accepted; complete or merge it first")

    def require_assignment_ready(self, task: Task) -> None:
        self.require_prerequisites(task)
        waits = self.open_wait_refs([task]).get(task.row_id, [])
        if waits:
            waiting = ", ".join(f"{ref.type[:-1]} {ref.id}" for ref in waits)
            raise Rejection(f"task {task.id} is unavailable: it still waits on {waiting}; let the wait finish before assigning it")

    def waiting(self, ref: Ref) -> Task | Question | Check:
        return self.awaitable[ref.type].find(ref.id)

    def is_wait_resolved(self, ref: Ref) -> bool:
        if ref.type == Plan.table():
            return PlanState(self.row_reader.row_state(ref)).is_closed()
        return self.waiting(ref).is_resolved()

    def waiting_ids(self, tasks: list[Task]) -> set[int]:
        return set(self.open_wait_refs(tasks))

    def open_wait_refs(self, tasks: list[Task]) -> dict[int, list[Ref]]:
        waits: dict[int, list[Ref]] = {}
        for link in self.links.model_links("source", tasks, WAIT_LINK):
            if not self.is_wait_resolved(link.target):
                waits.setdefault(link.source.id, []).append(link.target)
        return waits

    def blocked_without_wait(self) -> list[Task]:
        return self.selected(self.free_query(TaskState.BLOCKED, UNAPPROVED_PLAN_STATES).filter_absent(self.wait_links()))

    def wait_links(self) -> Query:
        return self.links.query().filter(link_type=WAIT_LINK).filter_ref("source", self.query())

    def broken_waits(self) -> list[tuple[Task, Check]]:
        return [(task, check) for check in self.checks.broken_waits() for task in self.waiting_refs(check)]

    def waiting_refs(self, model) -> list[Task]:
        return [task for ref in self.links.sources(model, WAIT_LINK) if ref.type == Task.table() and (task := self.find(ref.id)).state == TaskState.BLOCKED]

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
        return [number for number in numbers if self.matching(id=number, state=TaskState.OPEN) or self.matching(id=number, state=TaskState.STARTED)]

    def ready_waiting_tasks(self, model) -> list[Task]:
        return [task for task in self.waiting_refs(model) if not self.open_waits(task)]

    def unprioritised(self) -> list[Task]:
        planned = self.links.query().filter(link_type=PLAN_LINK).filter_ref("source", self.query())
        return self.selected(self.query().filter(state=TaskState.OPEN, delegated=False, priority=NORMAL, priority_set=False).filter_prefix("creator", AGENT_CREATOR).filter_absent(planned).order("id"))

    def environment_started_tasks(self, environment_id: int) -> list[Task]:
        return self.selected_globally(self.query().filter(environment_id=environment_id, state=TaskState.STARTED).order("id"))

    def agent_started(self) -> list[Task]:
        return self.selected(self.query().filter(state=TaskState.STARTED, delegated=False).order("id"))

    def other_started_tasks(self, current: Task | None) -> list[Task]:
        return [task for task in self.agent_started() if current is None or task.id != current.id]

    def tasks_numbered(self, ids: list[int]) -> list[Task]:
        return self.selected_globally(self.query().filter_listed("id", ids).order("id")) if ids else []

    def creator_tasks(self, ids: list[int], creator: Actor) -> list[Task]:
        return self.selected_globally(self.query().filter_listed("id", ids).filter(creator=creator).order("id")) if ids else []

    def open_tasks(self) -> list[Task]:
        return self.actionable(TaskState.OPEN)

    def blocked_tasks(self) -> list[Task]:
        return self.actionable(TaskState.BLOCKED)

    def testing_tasks(self) -> list[Task]:
        return self.selected(self.query().filter(state=TaskState.TESTING).order("id"))

    def actionable(self, state: TaskState) -> list[Task]:
        return self.free_tasks(state, UNAPPROVED_PLAN_STATES)

    def free_tasks(self, state: TaskState, plan_states: tuple[str, ...]) -> list[Task]:
        return self.selected(self.free_query(state, plan_states))

    def next_open_task(self) -> Task | None:
        return next(iter(self.next_open_tasks(1)), None)

    def next_open_tasks(self, count: int) -> list[Task]:
        query = self.free_query(TaskState.OPEN, UNAPPROVED_PLAN_STATES).filter_absent(self.user_paused_planned())
        return self.next_unblocked(query, count)

    def open_candidates(self) -> list[Task]:
        query = self.free_query(TaskState.OPEN, UNAPPROVED_PLAN_STATES).filter_absent(self.user_paused_planned())
        return self.next_unblocked(query, self.counted(query))

    def open_page_ids(self, rows: int) -> list[int]:
        return [task.row_id for task in self.next_unblocked(self.free_query(TaskState.OPEN, UNAPPROVED_PLAN_STATES), rows)]

    def next_unblocked(self, query: Query, count: int) -> list[Task]:
        selected, offset = [], 0
        while len(selected) < count:
            batch = self.selected(query.limit(PAGE_ROWS).offset(offset))
            if not batch:
                break
            blocked = self.unavailable_task_ids(batch)
            selected.extend(task for task in batch if task.row_id not in blocked)
            offset += len(batch)
        return selected[:count]

    def open_count(self) -> int:
        return self.counted(self.free_query(TaskState.OPEN, UNAPPROVED_PLAN_STATES))

    def unplanned_open_count(self) -> int:
        return self.counted(self.free_query(TaskState.OPEN, tuple(state.value for state in PlanState)))

    def has_stale_open(self, moment: datetime) -> bool:
        return self.counted(self.free_query(TaskState.OPEN, UNAPPROVED_PLAN_STATES).filter_less_equal("updated_at", moment)) > 0

    def user_paused_planned(self) -> Query:
        plans = Query.build(Plan).filter(state=PlanState.PAUSED.value, pauser=USER_PAUSER).filter_name_column(self.links.query(), "target")
        return self.links.query().filter(link_type=PLAN_LINK).filter_ref("source", self.query()).filter_existing(plans)

    def free_query(self, state: TaskState, plan_states: tuple[str, ...]) -> Query:
        plans = Query.build(Plan).filter_listed("state", list(plan_states)).filter_name_column(self.links.query(), "target")
        planned = self.links.query().filter(link_type=PLAN_LINK).filter_ref("source", self.query()).filter_existing(plans)
        return self.query().filter(state=state, delegated=False).filter_absent(planned).order_descending("priority").order("id")

    def completed_count_since(self, start: datetime) -> int:
        return self.counted(self.query().filter(state=TaskState.COMPLETED).filter_greater_equal("completed_at", start))

    def recent_completions(self, start: datetime, end: datetime) -> list[Task]:
        return self.selected(self.query().filter(state=TaskState.COMPLETED).filter_greater_equal("completed_at", start).filter_less("completed_at", end).order("id"))

    def with_state(self, state: TaskState) -> list[Task]:
        return self.matching(state=state)

    def current(self, agent: Agent) -> Task | None:
        return self.holder_task(Ref.build(agent))

    def holder_task(self, holder: Ref) -> Task | None:
        hand_links = self.links.query().filter(source=holder, link_type=CURRENT_TASK_LINK).filter_ref("target", self.query())
        tasks = self.selected_globally(self.query().filter_alternatives(self.query().filter(state=TaskState.STARTED), self.query().filter(delegated=True).filter_unlisted("state", list(CLOSED_STATES))).filter_existing(hand_links).order("id"))
        return next((task for task in tasks if task.is_started()), tasks[0] if tasks else None)

    def holder_task_ids(self, holder: Ref) -> tuple[int, ...]:
        return tuple(link.target.id for link in self.links.all_matching(source=holder, link_type=CURRENT_TASK_LINK))

    def last_task_id(self, holder: Ref) -> int:
        task_ids = self.recent_task_ids(holder, 1)
        return task_ids[-1] if task_ids else 0

    def recent_task_ids(self, holder: Ref, count: int) -> tuple[int, ...]:
        links = self.links.selected(self.links.query().filter(source=holder, link_type=CURRENT_TASK_LINK).order_descending("id").limit(count))
        return tuple(reversed([link.target.id for link in links]))

    def holder(self, task: Task) -> Ref | None:
        return self.task_holder(task.row_id)

    def task_holder(self, task_id: int) -> Ref | None:
        holders = self.links.ref_sources(Ref(Task.table(), task_id), CURRENT_TASK_LINK)
        return holders[-1] if holders else None

    def worker_assignment(self, task: Task) -> tuple[Ref, str] | None:
        target = Ref.build(task)
        return next(
            ((holder, link_type) for link_type in (CURRENT_TASK_LINK, FINISHED_LINK, QUEUED_LINK)
             for holder in self.links.ref_sources(target, link_type) if holder.type == WORKERS),
            None,
        )

    def delegated_refusal(self, task: Task) -> str:
        assignment = self.worker_assignment(task)
        if assignment is None:
            return f"task {task.id} is delegated without a worker assignment: inspect it with `journal task show {task.id}`"
        holder, link_type = assignment
        if link_type == QUEUED_LINK:
            return f"task {task.id} is queued for worker {holder.id}: remove it with `journal worker drain {holder.id}`"
        drop = " --drop" if self.finished_task_ids(holder) else ""
        command = f"journal worker release {holder.id}{drop}"
        if link_type == FINISHED_LINK:
            return f"task {task.id} has finished work from worker {holder.id} waiting to merge: release it with `{command}`"
        return f"task {task.id} is held by worker {holder.id}: release it with `{command}`"

    def agents_tasks(self, state: TaskState, agents: Query) -> list[Task]:
        return self.selected(self.agents_state_query(state, agents).order("id"))

    def agents_blocked_with(self, reason: str, agents: Query) -> list[Task]:
        return self.selected(self.agents_state_query(TaskState.BLOCKED, agents).filter(block_reason=reason).order("id"))

    def agents_state_query(self, state: TaskState, agents: Query) -> Query:
        agent_links = self.links.query().filter(link_type=CURRENT_TASK_LINK).filter_ref("target", self.query()).filter_existing(agents.filter_name_column(self.links.query(), "source"))
        return self.query().filter(state=state).filter_existing(agent_links)

    def row_holders(self, rows: list[Task]) -> dict[int, Ref]:
        return {link.target.id: link.source for link in self.links.model_links("target", rows, CURRENT_TASK_LINK)}

    def holder_started(self, started: Task, holder: Ref | None, actor: Actor) -> Task:
        with self.writing():
            self.assign_holder(started, holder, actor)
            if holder is not None and holder.type == Agent.table():
                agent = next(iter(self.agents.global_matching(id=holder.id)), None)
                if agent is None:
                    raise MissingRow(self.agents.table, holder.id)
                started = started.with_events(tuple(replace(event, session=agent.session) if isinstance(event, TaskStarted) else event for event in started.events))
            return self.save(started.with_(delegated=True) if holder is not None and holder.type == WORKERS else started, actor)

    def assign_holder(self, started: Task, holder: Ref | None, actor: Actor) -> None:
        if holder is None:
            return
        counterpart = self.holder_task(holder)
        if counterpart is not None and counterpart.id != started.id:
            raise Rejection(f"task {counterpart.id} is in hand: finish or pause it before task {started.id} is started")
        self.handover(started, holder, actor)

    def guard_worker_task(self, task: Task, holder: Ref | None, actor: Actor) -> None:
        owner = self.holder(task)
        if owner is not None and owner != holder and owner.type == WORKERS and not actor.can_move_worker_tasks():
            raise Rejection(self.delegated_refusal(task))

    def handover(self, task: Task, holder: Ref, actor: Actor) -> None:
        with self.writing():
            self.guard_worker_task(task, holder, actor)
            if task.started_at is None:
                self.require_assignment_ready(task)
            if holder.type == WORKERS:
                self.require_worker_assignment_room(task, holder)
            owner = self.holder(task)
            target = Ref.build(task)
            for link in self.links.all_matching(target=target, link_type=CURRENT_TASK_LINK):
                if link.source != holder:
                    self.links.delete(link, actor)
            if owner != holder:
                self.links.save(Link(source=holder, target=target, link_type=CURRENT_TASK_LINK), actor)
            if holder.type == WORKERS and not self.links.all_matching(source=holder, target=target, link_type=WORKED_LINK):
                self.links.save(Link(source=holder, target=target, link_type=WORKED_LINK), actor)
            if holder.type == WORKERS and not task.delegated:
                self.save(task.delegate(self.time_source.moment()), actor)
            for link in self.links.all_matching(source=holder, target=target, link_type=QUEUED_LINK):
                self.links.delete(link, actor)

    def queued(self, task: Task, worker: Ref, actor: Actor) -> Task:
        with self.writing():
            if not self.is_free(task):
                raise Rejection(f"task {task.id} is {task.state}: only an open task, or one in your hands, goes in a worker's queue")
            self.require_assignment_ready(task)
            self.require_worker_assignment_room(task, worker)
            if not self.links.all_matching(source=worker, target=Ref.build(task), link_type=QUEUED_LINK):
                self.links.save(Link(source=worker, target=Ref.build(task), link_type=QUEUED_LINK), actor)
            return self.save(task.delegate(self.time_source.moment()), actor)

    def queued_first(self, task: Task, worker: Ref, actor: Actor) -> Task:
        with self.writing():
            queue_links = self.links.all_matching(target=Ref.build(task), link_type=QUEUED_LINK)
            if not self.is_free(task) and not (task.delegated and queue_links):
                raise Rejection(f"task {task.id} is {task.state}: only an open task, one in your hands, or a queued one goes first")
            self.require_assignment_ready(task)
            self.require_worker_assignment_room(task, worker)
            for link in queue_links:
                self.links.delete(link, actor)
            remaining = [queued for queued in self.queue(worker) if queued.id != task.id]
            for link in self.links.all_matching(source=worker, link_type=QUEUED_LINK):
                self.links.delete(link, actor)
            for queued in (task, *remaining):
                self.links.save(Link(source=worker, target=Ref.build(queued), link_type=QUEUED_LINK), actor)
            return task if task.delegated else self.save(task.delegate(self.time_source.moment()), actor)

    def require_worker_assignment_room(self, task: Task, worker: Ref) -> None:
        if self.settings.option(EstimatesOptions.MODE) != "enforce":
            return
        value = wip_limit(self.settings.option(EstimatesOptions.WORKER_QUEUE_WIP_LIMIT), EstimatesOptions.WORKER_QUEUE_WIP_LIMIT.key)
        if value < 1:
            return
        assigned = {row.row_id for row in self.queue(worker)}
        assigned.update(self.holder_task_ids(worker))
        assigned.update(self.finished_task_ids(worker))
        if task.row_id in assigned or len(assigned) < value:
            return
        finished = set(self.finished_task_ids(worker))
        action = (f"merge worker {worker.id}'s finished work" if assigned & finished
                  else f"finish or release its current task or drain its queue with worker drain {worker.id}")
        raise Rejection(f"worker assignment WIP limit {value} full: {action}; then queue task {task.id}")

    def drop_holder(self, task: Task, holder: Ref | None, actor: Actor) -> None:
        if holder is None or holder.type == WORKERS or not task.is_started():
            return
        for link in self.links.all_matching(source=holder, target=Ref.build(task), link_type=CURRENT_TASK_LINK):
            self.links.delete(link, actor)

    def is_free(self, task: Task) -> bool:
        return (task.is_open() and not task.delegated) or (task.is_started() and self.holder(task) is None)

    def queue(self, worker: Ref) -> list[Task]:
        links = sorted(self.links.all_matching(source=worker, link_type=QUEUED_LINK), key=lambda link: link.row_id)
        return [self.find(n) for n in dict.fromkeys(link.target.id for link in links)]

    def ready_queue(self, worker: Ref) -> list[Task]:
        queue = self.queue(worker)
        unavailable = self.unavailable_task_ids(queue)
        return [task for task in queue if task.row_id not in unavailable]

    def worker_task(self, task_id: int, worker: int) -> Task:
        holdings = self.holder_task_ids(Ref(WORKERS, worker))
        if task_id not in holdings:
            raise Rejection(WORKER_TASK.format(task=task_id, worker=worker, holdings=", ".join(f"task {n}" for n in holdings) or "no task"))
        return self.find(task_id)

    def release(self, holder: Ref, actor: Actor) -> None:
        self.freed(holder, (CURRENT_TASK_LINK, FINISHED_LINK), actor)

    def release_all(self, holder: Ref, actor: Actor) -> None:
        self.freed(holder, (CURRENT_TASK_LINK, FINISHED_LINK, QUEUED_LINK), actor)

    def finish_holder_task(self, task_id: int, holder: Ref, actor: Actor) -> None:
        self.release_task(holder, task_id, actor)
        self.links.save(Link(source=holder, target=Ref("tasks", task_id), link_type=FINISHED_LINK), actor)

    def reopen_holder_task(self, task_id: int, holder: Ref, actor: Actor) -> None:
        for current in self.holder_task_ids(holder):
            self.finish_holder_task(current, holder, actor)
        for link in self.links.all_matching(source=holder, target=Ref("tasks", task_id), link_type=FINISHED_LINK):
            self.links.delete(link, actor)
        self.links.save(Link(source=holder, target=Ref("tasks", task_id), link_type=CURRENT_TASK_LINK), actor)

    def unfinished(self, holder: Ref, actor: Actor) -> None:
        for link in self.links.all_matching(source=holder, link_type=FINISHED_LINK):
            self.links.delete(link, actor)

    def finished_task_ids(self, holder: Ref) -> tuple[int, ...]:
        return tuple(link.target.id for link in sorted(self.links.all_matching(source=holder, link_type=FINISHED_LINK), key=lambda link: link.row_id))

    def release_task(self, holder: Ref, task_id: int, actor: Actor) -> None:
        for link in self.links.all_matching(source=holder, target=Ref("tasks", task_id), link_type=CURRENT_TASK_LINK):
            self.links.delete(link, actor)

    def unqueued_task(self, task: Task, actor: Actor) -> list[Ref]:
        queue_links = self.links.all_matching(target=Ref.build(task), link_type=QUEUED_LINK)
        for link in queue_links:
            self.links.delete(link, actor)
        if queue_links:
            self.save(task.with_(delegated=False), actor)
        return [link.source for link in queue_links]

    def unqueued(self, holder: Ref, actor: Actor) -> None:
        self.freed(holder, (QUEUED_LINK,), actor)

    def freed(self, holder: Ref, link_types: tuple[str, ...], actor: Actor) -> None:
        freed = []
        for link in (link for type_name in link_types for link in self.links.all_matching(source=holder, link_type=type_name)):
            self.links.delete(link, actor)
            freed += [task for task in self.matching(id=link.target.id, delegated=True) if not task.state.is_closed()]
        group = ReleasedTasks(holder.id, tuple(task.row_id for task in freed), self.common_plan(freed))
        for i, task in enumerate(freed):
            self.save(task.released(self.time_source.moment().timestamp(), group if i == 0 else None), actor)

    def common_plan(self, tasks: list[Task]) -> int:
        plans = {tuple(ref.id for ref in self.links.targets(task, PLAN_LINK)) for task in tasks}
        return plans.pop()[0] if len(plans) == 1 and len(next(iter(plans))) == 1 else 0

    def block_batch(self, start_at: float) -> list[Task]:
        return [task for task in self.selected(self.query().filter(state=TaskState.BLOCKED).filter_absent(self.wait_links())) if task.updated_at is not None and task.updated_at.timestamp() >= start_at]

    def has_worker_holder(self, task_ids: Sequence[int]) -> bool:
        return self.links.ref_count("target", [Ref(Task.table(), task_id) for task_id in task_ids], CURRENT_TASK_LINK, WORKERS) > 0

    def task_worker_holdings(self, task_ids: set[int]) -> dict[int, int]:
        refs = [Ref(Task.table(), task_id) for task_id in sorted(task_ids)]
        return {link.target.id: link.source.id for link in self.links.ref_links("target", refs, CURRENT_TASK_LINK) if link.source.type == WORKERS}

    def task_workers(self, task_ids: set[int]) -> set[int]:
        refs = [Ref(Task.table(), task_id) for task_id in sorted(task_ids)]
        queued = {link.source.id for link in self.links.ref_links("target", refs, QUEUED_LINK) if link.source.type == WORKERS}
        return {*self.task_worker_holdings(task_ids).values(), *queued}

    def worker_task_holdings(self, workers: list[Model]) -> dict[int, int]:
        return {link.target.id: link.source.id for link in self.links.model_links("source", workers, CURRENT_TASK_LINK)}

    def worker_holdings(self) -> dict[int, int]:
        return {link.target.id: link.source.id for link in self.links.selected(self.links.query().filter(link_type=CURRENT_TASK_LINK).filter_prefix("source", f"{WORKERS}:").order("id"))}

    def earlier_tasks(self, workers: list[Model], holdings: dict[int, int]) -> dict[int, int]:
        worker_tasks = {worker: task for task, worker in holdings.items()}
        return {link.source.id: link.target.id for link in self.links.model_links("source", workers, WORKED_LINK) if worker_tasks.get(link.source.id) != link.target.id}

    def worked_tasks(self, workers: list[Model]) -> dict[int, list[Task]]:
        links = sorted(self.links.model_links("source", workers, WORKED_LINK), key=lambda link: link.row_id)
        tasks = {task.row_id: task for task in self.numbered({link.target.id for link in links})}
        worked: dict[int, list[Task]] = {}
        for link in links:
            worked.setdefault(link.source.id, []).append(tasks[link.target.id])
        return worked

    def finished_ids(self, workers: list[Model]) -> dict[int, list[int]]:
        finished: dict[int, list[int]] = {}
        for link in sorted(self.links.model_links("source", workers, FINISHED_LINK), key=lambda link: link.row_id):
            finished.setdefault(link.source.id, []).append(link.target.id)
        return finished

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
        planned = self.links.query().filter(link_type=PLAN_LINK).filter_ref("source", self.query())
        return self.counted(self.query().filter_unlisted("state", CLOSED).filter_absent(planned))

    def unviewed(self) -> int:
        return self.counted(self.query().filter_unlisted("state", CLOSED).filter_missing_prefix("creator", USER_PREFIX))
