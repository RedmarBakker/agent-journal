from journal.features.sequences.sequences_nudges import SequencesNudges
from journal.features.sequences.states.following_sequence import FollowingSequence
from journal.features.tasks.states.ready import Ready
from journal.features.workers.workers_options import BUILDER_MODE
from tests.stories.builder.story_marks import story
from tests.stories.fixtures.main.sequence_run import SequenceRun

FIRST_STEP, SECOND_STEP = 1, 2


@story(SequenceRun, mode=BUILDER_MODE)
def test_the_user_skips_a_step_and_the_agent_is_given_the_next(story):
    story.user_skips_the_step()
    story.expect_agent_told(SequencesNudges.STEP_OMISSION, n=story.start.sequence, step=FIRST_STEP)
    story.expect_agent_told(SequencesNudges.PENDING_STEP, n=story.start.sequence, step=SECOND_STEP)
    story.expect_stack(Ready, FollowingSequence)


@story(SequenceRun, mode=BUILDER_MODE)
def test_the_user_skips_the_last_step_and_the_run_ends(story):
    story.user_skips_the_step()
    story.user_skips_the_step()
    story.expect_agent_told(SequencesNudges.STEP_OMISSION, n=story.start.sequence, step=SECOND_STEP)
    story.expect_agent_told(SequencesNudges.SEQUENCE_ENDED, n=story.start.sequence)
    story.expect_stack(Ready)


@story(SequenceRun, mode=BUILDER_MODE)
def test_the_user_ends_the_sequence(story):
    story.user_ends_the_sequence()
    story.expect_agent_told(SequencesNudges.SEQUENCE_CANCELLED, n=story.start.sequence)
    story.expect_stack(Ready)


@story(SequenceRun, mode=BUILDER_MODE)
def test_a_skip_while_the_run_is_paused_moves_on_to_the_next_step(story):
    story.agent_runs("sequence follow")
    story.agent_runs("sequence pause --why 'the user wants the footer first'")
    story.user_skips_the_step()
    story.expect_agent_told(SequencesNudges.PENDING_STEP, n=story.start.sequence, step=SECOND_STEP)
    story.expect_stack(Ready, FollowingSequence)


@story(SequenceRun, mode=BUILDER_MODE)
def test_a_skip_with_two_sequences_running_moves_the_top_one_only(story):
    inner = story.agent_creates_sequence("tag", "push the tag | write the notes")
    story.agent_runs(f"sequence run {inner}")
    story.user_skips_the_step()
    story.expect_agent_told(SequencesNudges.STEP_OMISSION, n=inner, step=FIRST_STEP)
    story.expect_agent_not_told(SequencesNudges.STEP_OMISSION, n=story.start.sequence)
    story.expect_stack(Ready, FollowingSequence, FollowingSequence)
