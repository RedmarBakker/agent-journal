from journal.features.sequences.sequences_nudges import SequencesNudges
from journal.features.sequences.states.following_sequence import FollowingSequence
from journal.features.tasks.states.ready import Ready
from journal.features.workers.workers_options import BUILDER_MODE
from tests.stories.builder.story_marks import story
from tests.stories.fixtures.main.guarded_sequence_run import GuardedSequenceRun
from tests.stories.fixtures.main.sequence_run import SequenceRun

FIRST_STEP = 1


@story(SequenceRun, mode=BUILDER_MODE)
def test_a_write_before_the_step_is_taken_up_is_refused(story):
    story.agent_writes("version.py")
    story.expect_refused(SequencesNudges.STEP_EDIT_BLOCK, n=story.start.sequence, step=FIRST_STEP)
    story.expect_stack(Ready, FollowingSequence)


@story(SequenceRun, mode=BUILDER_MODE)
def test_a_shell_run_before_the_step_is_taken_up_is_refused(story):
    story.agent_runs_in_the_shell("make build")
    story.expect_refused(SequencesNudges.STEP_EDIT_BLOCK, n=story.start.sequence, step=FIRST_STEP)
    story.expect_stack(Ready, FollowingSequence)


@story(SequenceRun, mode=BUILDER_MODE)
def test_taking_up_a_step_that_allows_edits_lets_the_writes_through(story):
    story.agent_runs("sequence follow")
    story.agent_writes("version.py")
    story.expect_allowed()
    story.expect_agent_not_told(SequencesNudges.STEP_EDIT_BLOCK, n=story.start.sequence)
    story.expect_stack(Ready, FollowingSequence)


@story(GuardedSequenceRun, mode=BUILDER_MODE)
def test_a_paused_run_holds_nothing_until_it_is_followed_again(story):
    story.agent_runs("sequence follow")
    story.agent_runs("sequence pause --why 'the user wants the footer first'")
    story.agent_writes("footer.py")
    story.expect_allowed()
    story.agent_runs("sequence follow")
    story.agent_writes("version.py")
    story.expect_refused(SequencesNudges.STEP_EDITS_WAIT, n=story.start.sequence, step=FIRST_STEP)
    story.expect_stack(Ready, FollowingSequence)
