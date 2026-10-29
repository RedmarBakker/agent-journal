from dataclasses import dataclass

from journal.engine.nudge import Nudge
from journal.engine.support.settings import Settings
from journal.engine.support.transition import Transition
from journal.events.rows.task_started import TaskStarted
from journal.features.plans.plans_nudges import PlansNudges
from journal.features.workers.states.orchestrating import Orchestrating


@dataclass(frozen=True)
class CoordinatingPlans(Orchestrating):
    """The main agent's floor while Plan agents replace the work modes: it orchestrates every plan and never writes code; the conduct of the new model is given to this state alone, so none of the old modes' conduct reaches it."""

    name = "coordinating_plans"
    title = "Coordinating plans"

    def mode_lines(self) -> tuple[Nudge, ...]:
        return (PlansNudges.COORDINATOR_MODE.create(),)

    def on_task_started(self, event: TaskStarted, settings: Settings) -> Transition:
        return self.none()
