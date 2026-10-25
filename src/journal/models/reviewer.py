from dataclasses import dataclass
from typing import ClassVar

from journal.events.rows.reviewer_ended import ReviewerEnded
from journal.models.helper import Helper
from journal.models.reviewer_state import ReviewerState


@dataclass(frozen=True)
class Reviewer(Helper):
    """An agent the journal sends itself, in orchestrator mode with the reviewer on, to review a clocked-out worker's work and report on each point to the agent that sent the worker; never a worker, and it never merges: its program and model, its session, the hash of the token its run proves itself with, its process, and whether it is reviewing, reported and waits idle for the next review, or ended without a report."""

    shared: ClassVar[bool] = False
    text_fields: ClassVar[tuple[str, ...]] = ("name", "brief")

    kind: str = "reviewer"
    state: ReviewerState = ReviewerState.REVIEWING

    def next_review(self, brief: str) -> "Reviewer":
        return self.with_(brief=brief, state=ReviewerState.REVIEWING, pid=0)

    def running_as(self, pid: int) -> "Reviewer":
        return self.with_(pid=pid)

    def reviewed(self) -> "Reviewer":
        return self.with_(state=ReviewerState.REVIEWED, token_hash="")

    def ended(self) -> "Reviewer":
        if self.state != ReviewerState.REVIEWING:
            return self
        return self.with_(state=ReviewerState.ENDED, token_hash="").with_event(ReviewerEnded(environment_id=self.environment_id))

    def is_reviewing(self) -> bool:
        return self.state == ReviewerState.REVIEWING
