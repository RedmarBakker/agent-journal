from dataclasses import dataclass

from journal.engine.base_state import BaseState
from journal.engine.support.settings import Settings
from journal.engine.support.transition import Transition
from journal.events.agent.subagent_ended import SubagentEnded
from journal.engine.no_task_assigner import NoTaskAssigner


@dataclass(frozen=True)
class Researching(BaseState):
    """A subagent of Claude Code at work on its own row, over Void from its start: it reads and answers, and its tool uses are its own, never the main agent's. Its end leaves it researching under the end of its session, so a message that resumes it finds it at work again."""

    name = "researching"
    assigner = NoTaskAssigner
    title = "Researching"

    def on_subagent_ended(self, event: SubagentEnded, settings: Settings) -> Transition:
        return self.none()
