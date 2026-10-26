from dataclasses import dataclass

from journal.engine.no_task_assigner import NoTaskAssigner
from journal.engine.base_state import BaseState
from journal.engine.support.settings import Settings
from journal.engine.support.transition import Transition
from journal.engine.support.typist import Typist
from journal.events.agent.session_started import SessionStarted
from journal.events.agent.prompt_submitted import PromptSubmitted
from journal.events.agent.stop import Stop
from journal.events.agent.tool_finished import ToolFinished
from journal.events.agent.tool_starting import ToolStarting
from journal.events.agent.turn_displayed import TurnDisplayed
from journal.events.feature_data import FeatureData
from journal.engine.nudge import Nudge


@dataclass(frozen=True)
class Compacting(BaseState):
    """The context is being compacted, until the agent shows it is not: the session starting again, a tool call or its end, the agent's words shown, a prompt or a stop pops it and hands that event to the state beneath, and so does a state pushed over it popping, so a compaction that ended without a start, or was cancelled, never holds the agent or keeps its lines from it. The state clears the typist's queue and disables it as it comes to the top, and enables it as it leaves the top: a line the journal would type in the meantime is dropped, and the look at the start after the compaction brings the agent up to date."""

    name = "compacting"
    assigner = NoTaskAssigner
    title = "Compacting"

    def on_enter(self, typist: Typist) -> None:
        typist.clear()
        typist.disable()

    def on_exit(self, typist: Typist) -> None:
        typist.enable()

    def takes_pushes(self) -> bool:
        return False

    def on_resume(self, data: FeatureData, settings: Settings) -> tuple[Nudge, ...] | Transition:
        return self.pop()

    def on_tool_finished(self, event: ToolFinished, settings: Settings) -> Transition:
        return self.forward()

    def on_turn_displayed(self, event: TurnDisplayed, settings: Settings) -> Transition:
        return self.forward()

    def on_tool_starting(self, event: ToolStarting, settings: Settings) -> Transition:
        return self.forward()

    def on_prompt_submitted(self, event: PromptSubmitted, settings: Settings) -> Transition:
        return self.forward()

    def on_stop(self, event: Stop, settings: Settings) -> Transition:
        return self.forward()

    def on_session_started(self, event: SessionStarted, settings: Settings) -> Transition:
        return self.forward()
