from dataclasses import dataclass

from journal.engine.base_state import BaseState
from journal.engine.support.settings import Settings
from journal.engine.support.transition import Transition
from journal.events.agent.subagent_ended import SubagentEnded


@dataclass(frozen=True)
class Researching(BaseState):
    """A subagent of Claude Code at work on its own row, over Void from its start and popped back to Void at its end: it reads and answers, and its tool uses are its own, never the main agent's."""

    name = "researching"
    title = "Researching"

    def on_subagent_ended(self, event: SubagentEnded, settings: Settings) -> Transition:
        return self.pop()
