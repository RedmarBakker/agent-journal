from dataclasses import dataclass

from journal.engine.base_state import BaseState
from journal.engine.support.settings import Settings
from journal.engine.support.transition import Transition
from journal.events.rows.plan_started import PlanStarted
from journal.events.rows.task_started import TaskStarted
from journal.features.plans.plans_part import PlansPart
from journal.features.tasks.states.working import Working


@dataclass(frozen=True)
class PlanWork(Working):
    """Working on a task with plans on: the current task joining the plan started here, or a plan starting with it, turns the work into the plan's; every other moment is Working's."""

    def plan_state(self, **fields) -> BaseState:
        raise NotImplementedError

    def on_task_started(self, event: TaskStarted, settings: Settings) -> Transition:
        started = event.data.part(PlansPart).started
        if started is None or event.task_id != self.task_id or event.task_id not in started.recent_tasks:
            return self.none()
        return self.swap(self.plan_state(plan_id=started.plan_id, task_id=self.task_id, approved=True, logged_at=self.logged_at, task_noun=self.task_noun))

    def on_plan_started(self, event: PlanStarted, settings: Settings) -> Transition:
        if event.task_id != self.task_id:
            return self.none()
        return self.swap(self.plan_state(plan_id=event.plan_id, task_id=self.task_id, approved=True, logged_at=self.logged_at, edits=self.edits, active_at=self.active_at, task_noun=self.task_noun))
