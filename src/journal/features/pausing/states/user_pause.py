from dataclasses import dataclass

from journal.engine.states.wait import Wait
from journal.engine.support.settings import Settings
from journal.engine.support.transition import Transition
from journal.events.agent.tool_starting import ToolStarting
from journal.events.rows.user_resumed import UserResumed
from journal.features.pausing.pausing_nudges import PausingNudges


@dataclass(frozen=True)
class UserPause(Wait):
    """The user paused the agent from the viewer: every tool call but a journal command is blocked until the user resumes it, since a pause stops the work and never the journaling, by the resume button, which pops it with the continue line, or by writing to it; a stop goes through, so a message sent in the meantime never deadlocks the agent between the block and the stop."""

    name = "paused"
    title = "Paused by you"

    def wait_description(self) -> tuple[str, str]:
        return "you to resume it", ""

    def blocks_tools(self) -> bool:
        return True

    def on_tool_starting(self, event: ToolStarting, settings: Settings) -> Transition:
        if event.call.is_journal:
            return self.none()
        return self.refuse(PausingNudges.PAUSED.create())

    def on_user_resumed(self, event: UserResumed, settings: Settings) -> Transition:
        return self.pop(PausingNudges.RESUMED.create()) if event.agent_session == event.session else self.none()

