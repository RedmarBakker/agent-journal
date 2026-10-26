from dataclasses import dataclass, replace

from journal.engine.base_state import BaseState
from journal.engine.nudge import Nudge
from journal.engine.support.block import Block
from journal.engine.support.settings import Settings
from journal.engine.support.transition import Transition
from journal.events.agent.stop import Stop
from journal.events.agent.tool_starting import ToolStarting
from journal.events.rows.plan_abandoned import PlanAbandoned
from journal.events.rows.plan_finished import PlanFinished
from journal.events.rows.plan_postponed import PlanPostponed
from journal.events.rows.task_closed import TaskClosed
from journal.events.rows.task_started import TaskStarted
from journal.features.plans.plans_nudges import PlansNudges
from journal.features.plans.plans_options import PlansOptions


@dataclass(frozen=True)
class NamingTestCommands(BaseState):
    """A plan's task waits here until the project names the commands that run its tests: reads and journal commands go through, every other tool and a stop are held with the line that says how to name them, and the state leaves by itself once the setting holds a line, or hands down its task's close and the plan's pause, cancel or end to the plan state beneath; another task started meanwhile becomes the one it waits for, never a second wait over it."""

    name = "naming_test_commands"
    title = "Naming the test commands"
    task_id: int = 0

    def on_push(self, settings: Settings) -> tuple[Nudge, ...] | Block:
        return (PlansNudges.TEST_COMMANDS_NEEDED.create(),)

    def on_tool_starting(self, event: ToolStarting, settings: Settings) -> Transition:
        if str(settings.value(PlansOptions.TEST_COMMANDS)).strip():
            return self.forward()
        if event.call.is_journal or not event.call.writes:
            return self.none()
        return self.refuse(PlansNudges.TEST_COMMANDS_NEEDED.create())

    def on_stop(self, event: Stop, settings: Settings) -> Transition:
        if str(settings.value(PlansOptions.TEST_COMMANDS)).strip():
            return self.pop()
        return self.refuse(PlansNudges.TEST_COMMANDS_NEEDED.create())

    def on_task_started(self, event: TaskStarted, settings: Settings) -> Transition:
        event.stop_propagation()
        return self.swap(replace(self, task_id=event.task_id))

    def on_task_closed(self, event: TaskClosed, settings: Settings) -> Transition:
        return self.forward() if event.task_id == self.task_id else self.none()

    def on_plan_postponed(self, event: PlanPostponed, settings: Settings) -> Transition:
        return self.forward()

    def on_plan_abandoned(self, event: PlanAbandoned, settings: Settings) -> Transition:
        return self.forward()

    def on_plan_finished(self, event: PlanFinished, settings: Settings) -> Transition:
        return self.forward()
