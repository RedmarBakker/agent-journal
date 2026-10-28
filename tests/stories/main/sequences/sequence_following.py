from journal.features.sequences.sequences_nudges import SequencesNudges
from journal.features.sequences.states.following_sequence import FollowingSequence
from journal.features.tasks.states.ready import Ready
from journal.features.tasks.states.working import Working
from journal.features.workers.workers_options import BUILDER_MODE
from journal.models.task_state import TaskState
from tests.stories.builder.story_marks import story
from tests.stories.fixtures.main.sequence_run import SequenceRun
from tests.stories.fixtures.main.started_task import StartedTask
from tests.stories.fixtures.main.working_agent import WorkingAgent

FIRST_STEP, SECOND_STEP = 1, 2


@story(SequenceRun, mode=BUILDER_MODE)
def test_a_step_never_taken_up_cannot_be_moved_on(story):
    story.agent_runs("sequence next")
    story.expect_command_refused()
    story.expect_agent_not_told(SequencesNudges.PENDING_STEP, n=story.start.sequence, step=SECOND_STEP)
    story.expect_stack(Ready, FollowingSequence)


@story(WorkingAgent, mode=BUILDER_MODE)
def test_a_sequence_of_one_step_ends_at_its_first_next(story):
    sequence = story.agent_creates_sequence("tag", "push the tag")
    story.agent_runs(f"sequence run {sequence}")
    story.agent_runs("sequence follow")
    story.agent_runs("sequence next")
    story.expect_agent_told(SequencesNudges.SEQUENCE_ENDED, n=sequence)
    story.expect_stack(Ready)


@story(SequenceRun, mode=BUILDER_MODE)
def test_running_the_running_sequence_again_starts_no_second_run(story):
    story.agent_runs(f"sequence run {story.start.sequence}")
    story.expect_stack(Ready, FollowingSequence)


@story(StartedTask, mode=BUILDER_MODE)
def test_a_sequence_runs_over_the_task_in_hand_and_gives_it_back_at_its_end(story):
    sequence = story.agent_creates_sequence("tag", "push the tag")
    story.agent_runs(f"sequence run {sequence}")
    story.expect_stack(Ready, Working, FollowingSequence)
    story.agent_runs("sequence follow")
    story.agent_runs("sequence next")
    story.expect_task(story.start.started_task, state=TaskState.STARTED)
    story.expect_stack(Ready, Working)


@story(SequenceRun, mode=BUILDER_MODE)
def test_sequence_show_lists_the_steps(story):
    story.agent_runs(f"sequence show {story.start.sequence}")
    story.expect_command_passed()
    story.expect_command_text("push the tag")
    story.expect_stack(Ready, FollowingSequence)
