from datetime import datetime, timezone

from journal.events.rows.task_closed import TaskClosed
from journal.events.listener import Listener
from journal.models.plan import Plan
from journal.models.plan_state import PlanState
from journal.models.support.ref import Ref
from journal.models.task import Task
from journal.support.actor import Actor
from journal.repositories.agents import Agents
from journal.repositories.plans import Plans
from journal.repositories.setting_rows import SettingRows
from journal.repositories.tasks import WORKERS, Tasks
from journal.features.plans.support.phase_testing import PhaseTesting
from journal.features.tasks.tasks_options import TasksOptions


class AdvancePlan(Listener[TaskClosed]):
    """A plan is done when its last task closes, whoever closes it, heard after the closed task's own mark is in the chat. For each started plan the closed task is in, by its plan link, the next task in the plan's order is started by writing its row, a paused one resumed before any other and none while a blocked one waits to be checked, assigned to the agent that had the closed one, or to the main agent when a worker had it or none did; at a checkpoint out of auto mode, at a phase end whose testing commands have not passed since, with no task that can start, or with that agent already on a task, nothing is written, and the state decides what to do."""

    def __init__(self, plans: Plans, tasks: Tasks, agents: Agents, settings: SettingRows, testing: PhaseTesting) -> None:
        self.plans, self.tasks, self.agents, self.settings, self.testing = plans, tasks, agents, settings, testing

    def handle(self, event: TaskClosed) -> None:
        task = self.tasks.find(event.task_id)
        if not task.is_closed():
            return
        time, actor = datetime.now(timezone.utc), Actor.parse(event.actor)
        for plan in self.plans.finished_plans(task):
            self.plans.save(plan.finished(time.timestamp()), actor)
        for plan in self.plans.started_plans(task):
            following, holder = self.plans.following_task(plan), self.next_holder(task)
            if following is not None and self.is_advancing(plan, holder):
                self.tasks.holder_started(following.plan_started(time, plan.row_id), holder, actor)

    def next_holder(self, task: Task) -> Ref | None:
        holder = self.tasks.holder(task)
        if holder is not None and holder.type != WORKERS:
            return holder
        present = self.agents.current()
        return None if present is None else Ref.build(present)

    def is_checkpoint_stop(self, plan: Plan) -> bool:
        return self.plans.checkpoint_plans(plan) is not None and not self.settings.option(TasksOptions.AUTO)

    def is_advancing(self, plan: Plan, holder: Ref | None) -> bool:
        return plan.state == PlanState.STARTED and not self.is_checkpoint_stop(plan) and not self.testing.unpassed(plan) and (holder is None or self.tasks.holder_task(holder) is None)
