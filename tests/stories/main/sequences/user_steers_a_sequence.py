from journal.features.sequences.sequences_nudges import SequencesNudges
from journal.features.sequences.states.following_sequence import FollowingSequence
from journal.features.tasks.states.ready import Ready
from journal.features.workers.workers_options import BUILDER_MODE
from journal.support.agent_role import AgentRole
from tests.stories.builder.story_marks import story
from tests.stories.fixtures.main.paused_sequence_run import PausedSequenceRun
from tests.stories.fixtures.main.sequence_run import SequenceRun

FIRST_STEP, SECOND_STEP = 1, 2


@story(SequenceRun, mode=BUILDER_MODE, scope=AgentRole.MAIN)
def test_the_user_skips_the_last_step_and_the_run_ends(story):
    story.user_skips_the_step()
    story.user_skips_the_step()
    story.expect_agent_told(SequencesNudges.STEP_OMISSION, n=story.start.sequence, step=SECOND_STEP)
    story.expect_agent_told(SequencesNudges.SEQUENCE_ENDED, n=story.start.sequence)
    story.expect_stack(Ready)


@story(SequenceRun, mode=BUILDER_MODE, scope=AgentRole.MAIN)
def test_the_user_ends_the_sequence(story):
    story.user_ends_the_sequence()
    story.expect_agent_told(SequencesNudges.SEQUENCE_CANCELLED, n=story.start.sequence)
    story.expect_stack(Ready)


@story(PausedSequenceRun, mode=BUILDER_MODE, scope=AgentRole.MAIN)
def test_a_skip_while_the_run_is_paused_moves_on_to_the_next_step(story):
    story.user_skips_the_step()
    story.expect_agent_told(SequencesNudges.PENDING_STEP, n=story.start.sequence, step=SECOND_STEP)
    story.expect_stack(Ready, FollowingSequence)
