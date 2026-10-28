from journal.features.reviewing.reviewing_options import ReviewingOptions
from journal.features.workers.states.orchestrating import Orchestrating
from tests.stories.fixtures.main.orchestrator_worker import OrchestratorWorker
from tests.stories.fixtures.state_fixture import StateFixture


class ReviewerAtWork(StateFixture):
    """With a reviewer on in orchestrator mode, the working worker proved both points and clocked out, so the journal sent a reviewer on its work, whose session started: start.reviewer."""

    stack = (Orchestrating,)

    parent = OrchestratorWorker

    settings = ((ReviewingOptions.REVIEWER, True),)

    def steps(self, story) -> None:
        story.worker_proves(self.worker, 1, "parser.py:12, test_reads passes")
        story.worker_proves(self.worker, 2, "parser.py:30, test_names passes")
        story.worker_clocks_out(self.worker, "the parser is done")
        self.reviewer = story.newest("reviewers")
        story.reviewer_session_starts(self.reviewer)

    def expected(self, story) -> None:
        story.expect_stack(Orchestrating)
