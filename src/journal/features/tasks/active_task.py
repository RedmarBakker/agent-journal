
from journal.support.caller import Caller
from journal.engine.clock import Clock
from journal.engine.support.session_agents import SessionAgents
from journal.models.support.ref import Ref
from journal.models.task import Task
from journal.support.rejection import Rejection
from journal.models.worker import Worker
from journal.repositories.agents import Agents
from journal.repositories.scope import Scope
from journal.repositories.tasks import Tasks
from journal.repositories.plans import Plans
from journal.support.time_source import TimeSource


class ActiveTask:
    """The work an agent has current, started and stopped in one place for the task and the work commands alike; a task started by an agent with another in hand pauses that one first; a task started is assigned to the worker that started it, whose hooks never reach the journal, to the agent whose session started it, or to the environment's working agent when the user started it; a task of an approved plan that is paused or not started yet starts its plan with it, so the plan is followed."""

    def __init__(self, tasks: Tasks, sessions: SessionAgents, agents: Agents, scope: Scope, clock: Clock, plans: Plans, time_source: TimeSource) -> None:
        self.time_source = time_source
        self.tasks, self.sessions, self.agents, self.scope, self.clock, self.plans = tasks, sessions, agents, scope, clock, plans

    def start(self, task: Task, caller: Caller) -> Task:
        for plan in self.plans.unapproved(task):
            plan.task_startable(task.id)
        holder = self.holder(caller)
        self.tasks.guard_worker_task(task, holder, caller.actor)
        if task.is_started() and self.tasks.holder(task) == holder:
            raise Rejection(f"task {task.id} is already in hand: it was started already")
        for plan in self.plans.unstarted_plans(task):
            self.plans.resume_plan(plan, task, caller.actor)
        return self.tasks.holder_started(task.started(self.time_source.moment()), holder, caller.actor)

    def paused_current(self, task: Task, caller: Caller) -> Task | None:
        holder = self.holder(caller)
        counterpart = self.tasks.holder_task(holder) if holder is not None and holder.type != Worker.table() else None
        if counterpart is None or counterpart.id == task.id or not counterpart.is_started():
            return None
        return self.tasks.save(counterpart.paused(f"task {task.id} was started", self.time_source.moment()), caller.actor)

    def holder(self, caller: Caller) -> Ref | None:
        if caller.is_worker():
            return Ref(Worker.table(), caller.worker_number)
        if caller.session is not None:
            return Ref.build(self.sessions.caller_agent(caller, caller.session, self.scope.id))
        present = self.agents.current()
        return None if present is None else Ref.build(present)
