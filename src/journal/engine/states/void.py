from dataclasses import dataclass

from journal.engine.no_task_assigner import NoTaskAssigner
from journal.engine.base_state import BaseState
from journal.engine.support.return_kinds import QUEUED
from journal.engine.engine_nudges import EngineNudges
from journal.engine.support.settings import Settings
from journal.engine.support.transition import Transition
from journal.events.agent.helper_assignment import HelperAssignment
from journal.events.agent.tool_starting import ToolStarting


@dataclass(frozen=True)
class Void(BaseState):
    """A helper's floor, never popped: no feature's conduct reaches it, no sequence starts on it, and every tool but a journal command is refused, a line that only changes folder or filters what the journal command prints counting as one, until the journal puts the helper to work by pushing its working state over it."""

    name = "void"
    assigner = NoTaskAssigner
    title = "Not at work"
    conduct_free = True
    decision_return = QUEUED

    def floored(self, mode: type[BaseState]) -> BaseState:
        return self

    def reset_states(self, states: tuple[BaseState, ...]) -> tuple[BaseState, ...]:
        return states[:2]

    def takes_pushes(self) -> bool:
        return False

    def on_tool_starting(self, event: ToolStarting, settings: Settings) -> Transition:
        if event.call.is_journal_line:
            return self.none()
        return self.refuse(EngineNudges.JOBLESS_HELPER.create())

    def on_helper_assignment(self, event: HelperAssignment, settings: Settings) -> Transition:
        return self.push(event.state)
