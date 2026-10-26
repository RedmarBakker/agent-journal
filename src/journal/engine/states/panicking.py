from dataclasses import dataclass
from typing import ClassVar

from journal.engine.no_task_assigner import NoTaskAssigner
from journal.engine.base_state import BaseState
from journal.engine.engine_nudges import EngineNudges
from journal.engine.nudge import Nudge
from journal.engine.support.settings import Settings
from journal.engine.support.transition import Transition
from journal.events.agent.prompt_submitted import PromptSubmitted
from journal.events.agent.tool_starting import ToolStarting


@dataclass(frozen=True)
class Panicking(BaseState):
    """The agent's stop was held five times in a row with nothing done between, so the journal is likely in a state it cannot leave: no feature's conduct is heard here, so the next stop goes through, and the agent is asked to set its state with journal panic and report what held it; a tool use or the user's message pops it."""

    name = "panicking"
    assigner = NoTaskAssigner
    title = "Held stops in a loop"
    conduct_free: ClassVar[bool] = True

    def on_push(self, settings: Settings) -> tuple[Nudge, ...]:
        return (EngineNudges.STOP_LOOP.create(),)

    def on_tool_starting(self, event: ToolStarting, settings: Settings) -> Transition:
        return self.forward()

    def on_prompt_submitted(self, event: PromptSubmitted, settings: Settings) -> Transition:
        return self.forward()
