from dataclasses import dataclass

from journal.engine.base_state import BaseState
from journal.engine.nudge import Nudge
from journal.engine.support.block import Block
from journal.engine.support.settings import Settings
from journal.engine.support.transition import Transition
from journal.events.agent.stop import Stop
from journal.events.agent.tool_starting import ToolStarting
from journal.features.plans.plans_nudges import PlansNudges
from journal.features.plans.plans_options import PlansOptions


@dataclass(frozen=True)
class NamingTestCommands(BaseState):
    """A plan's task waits here until the project names the commands that run its tests: reads and journal commands go through, every other tool and a stop are held with the line that says how to name them, and the state leaves by itself once the setting holds a line."""

    name = "naming_test_commands"
    title = "Naming the test commands"

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
