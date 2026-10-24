from datetime import datetime, timezone

from journal.support.caller import Caller
from journal.engine.clock import Clock
from journal.engine.support.session_agents import SessionAgents
from journal.features.tasks.states.working import Working
from journal.models.support.ref import Ref
from journal.models.task import Task
from journal.support.rejection import Rejection
from journal.models.task_state import TaskState
from journal.models.worker import Worker
from journal.repositories.agents import Agents
from journal.repositories.scope import Scope
from journal.support.missing_row import MissingRow
from journal.repositories.tasks import Tasks
from journal.repositories.plans import Plans


class ActiveTask:
    """The work an agent has current, started and stopped in one place for the task and the work commands alike; a task started is assigned to the worker that started it, whose hooks never reach the journal, to the agent whose session started it, or to the environment's working agent when the user started it."""

    def __init__(self, tasks: Tasks, sessions: SessionAgents, agents: Agents, scope: Scope, clock: Clock, plans: Plans) -> None:
        self.tasks, self.sessions, self.agents, self.scope, self.clock, self.plans = tasks, sessions, agents, scope, clock, plans

    def current(self, caller: Caller) -> Working | None:
        if caller.session is None:
            return None
        try:
            current = self.sessions.top(caller.session)
        except MissingRow:
            return None
        return current if isinstance(current, Working) else None

    def start(self, task: Task, caller: Caller) -> Task:
        for plan in self.plans.unapproved(task):
            plan.task_startable(task.id)
        holder = self.holder(caller)
        self.tasks.worker_hold_check(task, holder, caller.actor)
        if task.state == TaskState.STARTED and self.tasks.holder(task) == holder:
            raise Rejection(f"task {task.id} is already in hand: it was started already")
        return self.tasks.holder_started(task.started(datetime.now(timezone.utc)), holder, caller.actor)

    def holder(self, caller: Caller) -> Ref | None:
        if caller.worker_number is not None:
            return Ref(Worker.table(), caller.worker_number)
        if caller.session is not None:
            return Ref.build(self.sessions.agent(caller.session, self.scope.id))
        present = self.agents.current()
        return None if present is None else Ref.build(present)
