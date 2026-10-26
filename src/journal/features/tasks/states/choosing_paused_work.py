from dataclasses import dataclass, replace

from journal.engine.base_state import BaseState
from journal.engine.nudge import Nudge
from journal.engine.support.settings import Settings
from journal.engine.support.transition import Transition
from journal.events.agent.session_started import SessionStarted
from journal.events.agent.stop import Stop
from journal.events.feature_data import FeatureData
from journal.events.rows.paused_work_declined import PausedWorkDeclined
from journal.events.rows.plan_started import PlanStarted
from journal.events.rows.task_started import TaskStarted
from journal.features.tasks.tasks_nudges import TasksNudges
from journal.features.tasks.support.tasks_data import TasksData
from journal.features.tasks.tasks_part import TasksPart

CHOOSING_PAUSED_WORK = "choosing_paused_work"
# the stops the choice refuses before the first paused task, or the more urgent open one, is taken up for the agent
CHOICE_REFUSALS = 2


@dataclass(frozen=True)
class ChoosingPausedWork(BaseState):
    """A close left paused work the agent may take up beside an open task: pushed by the floor at the stop, it asks which to take up and holds nothing but the stop, the stop that pushes it counted as its first refusal. It ends when the agent starts a task or a plan, which go down to the floor, when the agent sets the paused work aside with journal task skip-paused or the user's own words do, or when there is nothing left to choose or the work mode switches; after its refusals the floor's assigner takes the first paused task up for the agent. It names no assigner, so the floor's keeps assigning beneath it."""

    name = CHOOSING_PAUSED_WORK
    title = "Choosing paused work"
    refusals: int = 0

    def on_resume(self, data: FeatureData, settings: Settings) -> tuple[Nudge, ...] | Transition:
        tasks = data.part(TasksPart)
        if tasks.current_task or not tasks.choosable:
            return self.pop()
        return (self.choice_line(tasks),)

    def is_mode_bound(self) -> bool:
        return True

    def on_task_started(self, event: TaskStarted, settings: Settings) -> Transition:
        if event.task_id not in event.data.part(TasksPart).agent_tasks:
            return self.none()
        event.stop_propagation()
        return self.forward()

    def on_plan_started(self, event: PlanStarted, settings: Settings) -> Transition:
        event.stop_propagation()
        return self.forward()

    def on_paused_work_declined(self, event: PausedWorkDeclined, settings: Settings) -> Transition:
        return self.pop() if event.agent_session == event.session else self.none()

    def on_stop(self, event: Stop, settings: Settings) -> Transition:
        tasks = event.data.part(TasksPart)
        if not tasks.choosable or not tasks.free_open:
            return self.pop()
        if event.prior_refusal or self.refusals >= CHOICE_REFUSALS:
            return self.none()
        return Transition.merged(self, [self.swap(replace(self, refusals=self.refusals + 1)), self.refuse(self.choice_line(tasks))])

    def on_session_started(self, event: SessionStarted, settings: Settings) -> Transition:
        tasks = event.data.part(TasksPart)
        return self.none(self.choice_line(tasks)) if tasks.choosable else self.pop()

    @staticmethod
    def choice_line(tasks: TasksData) -> Nudge:
        blocked = f"; blocked, for your information: {tasks.blocked_without_wait_summary}" if tasks.blocked_without_wait else ""
        return TasksNudges.PAUSED_CHOICE.create(tasks=tasks.choosable_summary, blocked=blocked)
