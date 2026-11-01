from dataclasses import dataclass

from journal.engine.nudge import Nudge
from journal.engine.support.settings import Settings
from journal.engine.support.transition import Transition
from journal.events.agent.session_started import SessionStarted
from journal.events.agent.tool_starting import ToolStarting
from journal.features.plans.plans_nudges import PlansNudges
from journal.features.plans.states.plans_working import PlansWorking
from journal.features.plans.states.plans_ready import PlansReady


@dataclass(frozen=True)
class LeadingTaskWorking(PlansWorking):
    """Working on a task outside a plan."""

    name = "leading_task_working"
    title = "Working a task alone"

@dataclass(frozen=True)
class LeadingTask(PlansReady):
    """The floor of an agent working a task outside every plan: a session start puts it to work on its task."""

    name = "leading_task"
    title = "Working a task alone"

    task_id: int = 0

    @classmethod
    def keeps_floor(cls) -> bool:
        return True

    def subject(self) -> str:
        return f"task {self.task_id}"

    def working_state(self, **fields) -> LeadingTaskWorking:
        return LeadingTaskWorking(**fields)

    def on_session_started(self, event: SessionStarted, settings: Settings) -> Transition:
        active = self.active(event.time)
        return active.push(active.working_state(task_id=self.task_id, logged_at=event.time), PlansNudges.WORKING_TASK_ALONE.create(task=self.task_id))
