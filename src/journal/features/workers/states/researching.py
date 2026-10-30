from dataclasses import dataclass

from journal.engine.base_state import BaseState
from journal.engine.support.settings import Settings
from journal.engine.support.transition import Transition
from journal.events.agent.subagent_ended import SubagentEnded
from journal.events.agent.tool_starting import ToolStarting
from journal.features.workers.workers_nudges import WorkersNudges
from journal.engine.no_task_assigner import NoTaskAssigner


@dataclass(frozen=True)
class Researching(BaseState):
    """A subagent of Claude Code at work on its own row, over Void from its start: it reads and answers, a shell command that is more than a read or a search refused, and its tool uses are its own, never the main agent's. Its end leaves it researching under the end of its session, so a message that resumes it finds it at work again."""

    name = "researching"
    assigner = NoTaskAssigner
    title = "Researching"

    def on_tool_starting(self, event: ToolStarting, settings: Settings) -> Transition:
        refused = next((part for part in event.call.parts if not part.is_journal and not part.classification.is_read), None)
        return self.refuse(WorkersNudges.SUBAGENT_COMMAND_REFUSAL.create(command=refused.text)) if refused else self.none()

    def on_subagent_ended(self, event: SubagentEnded, settings: Settings) -> Transition:
        return self.none()
