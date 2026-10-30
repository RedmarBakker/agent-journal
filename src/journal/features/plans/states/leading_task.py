from dataclasses import dataclass

from journal.engine.nudge import Nudge
from journal.engine.support.settings import Settings
from journal.engine.support.transition import Transition
from journal.events.agent.session_started import SessionStarted
from journal.events.agent.tool_starting import ToolStarting
from journal.features.plans.plans_nudges import PlansNudges
from journal.features.plans.states.plans_working import PlansWorking
from journal.features.workers.states.soloing import Soloing


@dataclass(frozen=True)
class LeadingTaskWorking(PlansWorking, Soloing):
    """Working on the standalone task while applying Soloing's worker dispatch refusal."""

    name = "leading_task_working"
    title = "Working a task alone"

    def on_tool_starting(self, event: ToolStarting, settings: Settings) -> Transition:
        solo = Soloing.on_tool_starting(self, event, settings)
        return solo if solo.refusal else super().on_tool_starting(event, settings)


@dataclass(frozen=True)
class LeadingTask(Soloing):
    """The floor of the agent of a task outside every plan, worked alone in the task's own environment as a one-task solo plan is: no work mode replaces it, and a session start puts the agent to work on its task, saying so; every other moment is Soloing's."""

    name = "leading_task"
    title = "Working a task alone"

    task_id: int = 0

    @classmethod
    def keeps_floor(cls) -> bool:
        return True

    def subject(self) -> str:
        return f"task {self.task_id}"

    def mode_lines(self) -> tuple[Nudge, ...]:
        return ()

    def working_state(self, **fields) -> LeadingTaskWorking:
        return LeadingTaskWorking(**fields)

    def on_session_started(self, event: SessionStarted, settings: Settings) -> Transition:
        active = self.active(event.time)
        return active.push(active.working_state(task_id=self.task_id, logged_at=event.time), PlansNudges.WORKING_TASK_ALONE.create(task=self.task_id))
