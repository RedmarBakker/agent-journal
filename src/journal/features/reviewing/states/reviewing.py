from dataclasses import dataclass

from journal.engine.base_state import BaseState
from journal.engine.states.ended import Ended
from journal.engine.support.settings import Settings
from journal.engine.support.transition import Transition
from journal.events.agent.stop import Stop
from journal.events.agent.tool_starting import ToolStarting
from journal.events.rows.worker_reviewed import WorkerReviewed
from journal.features.reviewing.reviewing_nudges import ReviewingNudges
from journal.engine.no_task_assigner import NoTaskAssigner


@dataclass(frozen=True)
class Reviewing(BaseState):
    """A reviewer at its one job, which it never leaves: reviewing a clocked-out worker's work. It reads and runs the tests, but every file edit is refused, it hears no feature's conduct, its stop is refused until it gives its report, and its report ends its session."""

    name = "reviewing"
    assigner = NoTaskAssigner
    title = "Reviewing a worker's work"
    conduct_free = True

    def on_tool_starting(self, event: ToolStarting, settings: Settings) -> Transition:
        return self.refuse(ReviewingNudges.REVIEWER_WRITES.create()) if event.call.writes else self.none()

    def on_stop(self, event: Stop, settings: Settings) -> Transition:
        return self.refuse(ReviewingNudges.REPORT_REQUEST.create())

    def on_worker_reviewed(self, event: WorkerReviewed, settings: Settings) -> Transition:
        return self.push(Ended()) if event.reviewer_session == event.session else self.none()
