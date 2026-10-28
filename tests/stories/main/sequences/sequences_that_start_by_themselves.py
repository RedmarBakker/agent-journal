from journal.features.sequences.sequences_nudges import SequencesNudges
from journal.features.sequences.states.following_sequence import FollowingSequence
from journal.features.tasks.states.ready import Ready
from journal.features.workers.workers_options import BUILDER_MODE
from tests.stories.builder.story_marks import story
from tests.stories.fixtures.main.working_agent import WorkingAgent

FIRST_STEP = 1


@story(WorkingAgent, mode=BUILDER_MODE)
def test_a_plan_the_user_creates_starts_no_sequence(story):
    story.user_creates_plan("the shop", "the shop sells")
    story.expect_agent_not_told(SequencesNudges.PENDING_STEP)
    story.expect_stack(Ready)


@story(WorkingAgent, mode=BUILDER_MODE)
def test_the_users_phrase_as_a_prompt_starts_its_sequence(story):
    story.agent_is_prompted("give me an update")
    story.expect_agent_told(SequencesNudges.PENDING_STEP, step=FIRST_STEP)
    story.expect_stack(Ready, FollowingSequence)


@story(WorkingAgent, mode=BUILDER_MODE)
def test_words_that_are_no_trigger_phrase_start_nothing(story):
    story.agent_is_prompted("how is the footer coming along?")
    story.expect_agent_not_told(SequencesNudges.PENDING_STEP)
    story.expect_stack(Ready)


@story(WorkingAgent, mode=BUILDER_MODE)
def test_the_same_phrase_twice_starts_one_run(story):
    story.agent_is_prompted("give me an update")
    story.agent_is_prompted("give me an update")
    story.expect_stack(Ready, FollowingSequence)
