from journal.features.sequences.sequences_nudges import SequencesNudges
from journal.features.sequences.states.following_sequence import FollowingSequence
from journal.features.tasks.states.ready import Ready
from journal.models.plan_state import PlanState
from journal.support.agent_role import AgentRole
from tests.stories.builder.story_marks import story
from tests.stories.fixtures.main.draft_plan import DraftPlan


@story(DraftPlan, subject=AgentRole.MAIN)
def test_a_cancelled_plan_ends_the_run_that_builds_it_and_says_why(story):
    result = story.user_cancels_plan(story.plans.first)
    story.expect_plan(story.plans.first, state=PlanState.CANCELLED)
    result.expect_agent_told(story.agents.subject, SequencesNudges.SEQUENCE_CANNOT_FINISH)
    story.expect_stack(story.agents.subject, Ready)


@story(DraftPlan, subject=AgentRole.MAIN)
def test_a_cancelled_plan_leaves_a_run_about_another_plan_as_it_was(story):
    other = story.user_creates_plan("the shop", "the shop sells")
    result = story.user_cancels_plan(other)
    story.expect_plan(story.plans.first, state=PlanState.DRAFT)
    result.expect_agent_not_told(story.agents.subject, SequencesNudges.SEQUENCE_CANNOT_FINISH)
    story.expect_stack(story.agents.subject, Ready, FollowingSequence)
