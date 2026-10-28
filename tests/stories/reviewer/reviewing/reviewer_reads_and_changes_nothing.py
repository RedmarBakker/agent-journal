from journal.engine.states.void import Void
from journal.features.reviewing.reviewing_nudges import ReviewingNudges
from journal.features.reviewing.states.reviewing import Reviewing
from journal.features.workers.workers_options import ORCHESTRATOR_MODE
from tests.stories.builder.story_marks import story
from tests.stories.fixtures.reviewer.reviewer_at_work import ReviewerAtWork


@story(ReviewerAtWork, mode=ORCHESTRATOR_MODE)
def test_a_reviewer_reads_and_is_refused_a_write(story):
    story.agent_reads()
    story.expect_allowed()
    story.agent_writes("parser.py")
    story.expect_refused(ReviewingNudges.REVIEWER_WRITES)
    story.expect_stack(Void, Reviewing)


@story(ReviewerAtWork, mode=ORCHESTRATOR_MODE)
def test_a_reviewer_stopping_before_its_report_is_refused(story):
    story.agent_stops()
    story.expect_refused(ReviewingNudges.REPORT_REQUEST)
    story.expect_stack(Void, Reviewing)
