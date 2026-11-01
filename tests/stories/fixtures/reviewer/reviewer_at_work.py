from journal.features.reviewing.reviewing_options import ReviewingOptions
from journal.features.tasks.states.external_wait import ExternalWait
from journal.features.tasks.states.ready import Ready
from tests.stories.fixtures.worker.working_worker import WorkingWorker
from tests.stories.fixtures.state_fixture import StateFixture


class ReviewerAtWork(StateFixture):
    """With the reviewer on, the working worker proved both points and clocked out, so the journal sent a reviewer on its work, whose session started: story.agents.reviewers.first()."""

    stack = (Ready,)

    parent = WorkingWorker

    settings = ((ReviewingOptions.REVIEWER, True),)

    def steps(self, story) -> None:
        story.agent_proves(story.agents.workers.first(), 1, "parser.py:12, test_reads passes")
        story.agent_proves(story.agents.workers.first(), 2, "parser.py:30, test_names passes")
        story.agent_clocks_out(story.agents.workers.first(), "the parser is done")
        self.reviewers.first = story.newest("reviewers")
        story.agent_starts_a_session(story.agents.reviewers.first())

    def expected(self, story) -> None:
        story.expect_stack(story.agents.main, Ready, ExternalWait)
