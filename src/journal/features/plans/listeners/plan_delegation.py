from journal.events.listener import Listener
from journal.events.models.updated import Updated
from journal.models.plan import Plan
from journal.models.plan_state import PlanState
from journal.models.task import Task
from journal.repositories.plans import Plans
from journal.support.actor import Actor
from journal.support.time_source import TimeSource
from journal.features.workers.support.work_mode import WorkMode

MOVES = {PlanState.STARTED: Plan.reopened, PlanState.DELEGATED: Plan.delegated, PlanState.PAUSED: lambda plan, time: plan.postponed(time, False)}


class PlanDelegation(Listener[Updated]):
    """A plan's state follows who works its tasks: the agent starting one of them makes it its active plan, one of them handed to a worker while the agent holds none makes it delegated, which is no active plan, and a delegated plan whose last worker task closes is paused again; an orchestrator keeps all its plans started, so its plans are left as they are."""

    def __init__(self, plans: Plans, time_source: TimeSource, work_mode: WorkMode) -> None:
        self.plans, self.time_source, self.work_mode = plans, time_source, work_mode

    def handle(self, event: Updated) -> None:
        task, previous = event.model, event.previous_row(Task)
        if self.work_mode.delegates_work() or not isinstance(task, Task) or previous is None or (task.state, task.delegated) == (previous.state, previous.delegated):
            return
        for plan in self.plans.working_plans(task):
            self.state_update(plan, task, previous)

    def state_update(self, plan: Plan, task: Task, previous: Task) -> None:
        wanted = self.wanted_state(plan, task, previous)
        if wanted is not None and wanted != plan.state:
            self.plans.save(MOVES[wanted](plan, self.time_source.seconds()), Actor.system())

    def wanted_state(self, plan: Plan, task: Task, previous: Task) -> PlanState | None:
        if task.is_started() and not task.delegated:
            return PlanState.STARTED
        if task.delegated and not previous.delegated and not self.plans.has_agent_task(plan):
            return PlanState.DELEGATED
        if task.delegated and task.is_closed() and plan.state == PlanState.DELEGATED and not self.plans.has_worker_task(plan):
            return PlanState.PAUSED
        return None
