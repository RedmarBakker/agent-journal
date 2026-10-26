from dataclasses import dataclass

from journal.engine.base_state import BaseState
from journal.engine.engine_nudges import EngineNudges
from journal.engine.support.settings import Settings
from journal.engine.support.transition import Transition
from journal.events.agent.helper_assignment import HelperAssignment
from journal.events.agent.tool_starting import ToolStarting


@dataclass(frozen=True)
class Void(BaseState):
    """A helper's floor, never popped: no feature's conduct reaches it and every tool but a journal command is refused, until the journal puts the helper to work by pushing its working state over it."""

    name = "void"
    title = "Not at work"
    conduct_free = True

    def on_tool_starting(self, event: ToolStarting, settings: Settings) -> Transition:
        if event.call.is_journal:
            return self.none()
        return self.refuse(EngineNudges.JOBLESS_HELPER.create())

    def on_helper_assignment(self, event: HelperAssignment, settings: Settings) -> Transition:
        return self.push(event.state)
