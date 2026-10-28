from journal.engine.states.ended import Ended
from journal.engine.states.void import Void
from journal.features.reviewing.reviewing_nudges import ReviewingNudges
from journal.features.reviewing.states.reviewing import Reviewing
from journal.features.workers.workers_nudges import WorkersNudges
from journal.features.workers.workers_options import ORCHESTRATOR_MODE
from journal.support.agent_role import AgentRole
from tests.stories.builder.story_marks import story
from tests.stories.fixtures.reviewer.reviewer_at_work import ReviewerAtWork


@story(ReviewerAtWork, mode=ORCHESTRATOR_MODE, scope=AgentRole.REVIEWER)
def test_a_report_that_passes_every_point_signs_the_work_off_and_ends_the_reviewer(story):
    story.agent_runs("review record '1 passed. 2 passed.'")
    story.expect_command_passed()
    story.expect_main_told(WorkersNudges.IDLE_WORKER)
    story.expect_stack(Void, Reviewing, Ended)


@story(ReviewerAtWork, mode=ORCHESTRATOR_MODE, scope=AgentRole.REVIEWER)
def test_a_report_that_leaves_a_point_undecided_goes_to_the_agent_to_decide(story):
    story.agent_runs("review record '1 passed. 2 undecided: the grammar file is missing.'")
    story.expect_command_passed()
    story.expect_main_told(ReviewingNudges.REVIEW_UNDECIDED)
    story.expect_stack(Void, Reviewing, Ended)


@story(ReviewerAtWork, mode=ORCHESTRATOR_MODE, scope=AgentRole.REVIEWER)
def test_only_the_reviewer_records_a_review(story):
    story.main_agent_runs("review record '1 passed. 2 passed.'")
    story.expect_command_refused()
    story.expect_stack(Void, Reviewing)
