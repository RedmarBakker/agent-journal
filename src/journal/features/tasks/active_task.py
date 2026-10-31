
from journal.support.caller import Caller
from journal.engine.clock import Clock
from journal.features.estimates.support.work_in_progress import WorkInProgress
from journal.models.support.ref import Ref
from journal.models.task import Task
from journal.models.task_state import TaskState
from journal.support.rejection import Rejection
from journal.models.worker import Worker
from journal.support.actor import Actor
from journal.repositories.agents import Agents
from journal.repositories.tasks import Tasks
from journal.repositories.plans import Plans
from journal.features.tasks.support.waits import Waits
from journal.support.time_source import TimeSource


class ActiveTask:
    """The work an agent has current, started and stopped in one place for the task and the work commands alike; a task started by an agent with another in hand blocks that one on it first, so it opens again once the started one closes; a task started is assigned to the worker that started it, whose hooks never reach the journal, to the agent whose session started it, or to the environment's working agent when the user started it; a task of an approved plan that is paused or not started yet starts its plan with it, so the plan is followed."""

    def __init__(self, tasks: Tasks, agents: Agents, clock: Clock, plans: Plans,
                 time_source: TimeSource, flow: WorkInProgress, waits: Waits) -> None:
        self.time_source, self.waits = time_source, waits
        self.tasks, self.agents, self.clock, self.plans, self.flow = tasks, agents, clock, plans, flow

    def start(self, task: Task, caller: Caller) -> tuple[Task, Task | None]:
        with self.tasks.writing():
            holder = self.prepare_start(task, caller, caller.actor)
            if task.state == TaskState.BLOCKED:
                self.waits.released(task, caller.actor)
            previous = self.blocked_current(task, caller)
            return self.start_ready(task, holder, caller.actor), previous

    def start_as(self, task: Task, caller: Caller, actor: Actor) -> Task:
        with self.tasks.writing():
            holder = self.prepare_start(task, caller, actor)
            return self.start_ready(task, holder, actor)

    def prepare_start(self, task: Task, caller: Caller, actor: Actor) -> Ref | None:
        for plan in self.plans.unapproved(task):
            plan.task_startable(task.id)
        self.tasks.require_prerequisites(task)
        self.require_start(task)
        holder = self.holder(caller)
        self.tasks.guard_worker_task(task, holder, actor)
        if task.is_started() and self.tasks.holder(task) == holder:
            raise Rejection(f"task {task.id} is already in hand: it was started already")
        return holder

    def start_ready(self, task: Task, holder: Ref | None, actor: Actor) -> Task:
        for plan in self.plans.unstarted_plans(task):
            self.plans.resume_plan(plan, task, actor)
        return self.tasks.holder_started(task.started(self.time_source.moment()), holder, actor)

    def require_start(self, task: Task) -> None:
        self.flow.require_start(task)

    def blocked_current(self, task: Task, caller: Caller) -> Task | None:
        holder = self.holder(caller)
        counterpart = self.tasks.holder_task(holder) if holder is not None and holder.type != Worker.table() else None
        if counterpart is None or counterpart.id == task.id or not counterpart.is_started():
            return None
        blocked = self.tasks.save(counterpart.blocked("", self.time_source.moment()), caller.actor)
        self.waits.linked(blocked, [f"task:{task.id}"], "", 0, caller.actor)
        return blocked

    def holder(self, caller: Caller) -> Ref | None:
        caller_holder = caller.holder_ref()
        if caller_holder is not None:
            return caller_holder
        present = self.agents.current()
        return None if present is None else Ref.build(present)
