from dataclasses import dataclass

from journal.engine.nudge import Nudge
from journal.engine.support.settings import Settings
from journal.engine.support.transition import Transition
from journal.events.agent.tool_starting import ToolStarting
from journal.features.plans.states.plans_ready import PlansReady
from journal.features.workers.workers_nudges import WorkersNudges

DISPATCHES = ("journal worker dispatch", "journal worker send")


@dataclass(frozen=True)
class Soloing(PlansReady):
    """The solo mode state: the agent does everything itself, and a worker's dispatch is refused."""

    name = "soloing"
    title = "Working alone"

    def mode_lines(self) -> tuple[Nudge, ...]:
        return (WorkersNudges.SOLO_MODE.create(),)

    def on_tool_starting(self, event: ToolStarting, settings: Settings) -> Transition:
        if any(part.text.startswith(DISPATCHES) for part in event.call.parts):
            return self.refuse(WorkersNudges.SOLO_DISPATCH.create())
        return super().on_tool_starting(event, settings)
