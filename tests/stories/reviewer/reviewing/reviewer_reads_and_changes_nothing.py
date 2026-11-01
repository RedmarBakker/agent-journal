from journal.engine.states.void import Void
from journal.features.reviewing.reviewing_nudges import ReviewingNudges
from journal.features.reviewing.states.reviewing import Reviewing
from journal.support.agent_role import AgentRole
from tests.stories.builder.story_marks import story
from tests.stories.fixtures.reviewer.reviewer_at_work import ReviewerAtWork


@story(ReviewerAtWork, subject=AgentRole.REVIEWER)
def test_a_reviewer_reads_and_is_refused_a_write(story):
    result = story.agent_reads(story.agents.subject)
    result.expect_allowed()
    result = story.agent_writes(story.agents.subject, "parser.py")
    result.expect_refused(story.agents.subject, ReviewingNudges.REVIEWER_WRITES)
    story.expect_stack(story.agents.subject, Void, Reviewing)


@story(ReviewerAtWork, subject=AgentRole.REVIEWER)
def test_a_reviewer_stopping_before_its_report_is_refused(story):
    result = story.agent_stops(story.agents.subject)
    result.expect_refused(story.agents.subject, ReviewingNudges.REPORT_REQUEST)
    story.expect_stack(story.agents.subject, Void, Reviewing)


@story(ReviewerAtWork, subject=AgentRole.REVIEWER)
def test_a_reviewer_may_not_say_it_is_stuck(story):
    result = story.agent_runs(story.agents.subject, "stuck 'lost'")
    result.expect_command_refused()
    story.expect_stack(story.agents.subject, Void, Reviewing)
