from journal.features.sequences.sequences_nudges import SequencesNudges
from journal.features.sequences.states.following_sequence import FollowingSequence
from journal.features.tasks.states.ready import Ready
from journal.features.workers.workers_options import BUILDER_MODE
from journal.models.plan_state import PlanState
from tests.stories.builder.story_marks import story
from tests.stories.fixtures.main.draft_plan import DraftPlan


@story(DraftPlan, mode=BUILDER_MODE)
def test_a_cancelled_plan_ends_the_run_that_builds_it_and_says_why(story):
    story.user_cancels_plan(story.start.plan)
    story.expect_plan(story.start.plan, state=PlanState.CANCELLED)
    story.expect_agent_told(SequencesNudges.SEQUENCE_CANNOT_FINISH)
    story.expect_stack(Ready)


@story(DraftPlan, mode=BUILDER_MODE)
def test_a_cancelled_plan_leaves_a_run_about_another_plan_as_it_was(story):
    other = story.user_creates_plan("the shop", "the shop sells")
    story.user_cancels_plan(other)
    story.expect_plan(story.start.plan, state=PlanState.DRAFT)
    story.expect_agent_not_told(SequencesNudges.SEQUENCE_CANNOT_FINISH)
    story.expect_stack(Ready, FollowingSequence)
