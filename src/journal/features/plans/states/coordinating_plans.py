from dataclasses import dataclass

from journal.engine.nudge import Nudge
from journal.engine.support.settings import Settings
from journal.engine.support.transition import Transition
from journal.events.rows.plan_started import PlanStarted
from journal.events.rows.task_started import TaskStarted
from journal.features.plans.plans_nudges import PlansNudges
from journal.features.plans.states.plans_ready import PlansReady


@dataclass(frozen=True)
class CoordinatingPlans(PlansReady):
    """The main agent's floor while Plan agents are on: it coordinates each plan through its agent and writes no code or worker of its own."""

    name = "coordinating_plans"
    title = "Coordinating plans"

    def floor_lines(self) -> tuple[Nudge, ...]:
        return (PlansNudges.COORDINATOR_MODE.create(),)

    def on_task_started(self, event: TaskStarted, settings: Settings) -> Transition:
        return self.none()

    def on_plan_started(self, event: PlanStarted, settings: Settings) -> Transition:
        return self.none()
