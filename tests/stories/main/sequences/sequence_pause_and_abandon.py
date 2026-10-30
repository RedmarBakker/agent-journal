from journal.features.sequences.sequences_nudges import SequencesNudges
from journal.features.sequences.states.following_sequence import FollowingSequence
from journal.features.tasks.states.ready import Ready
from journal.features.workers.workers_options import BUILDER_MODE
from journal.support.agent_role import AgentRole
from tests.stories.builder.story_marks import story
from tests.stories.fixtures.main.paused_sequence_run import PausedSequenceRun
from tests.stories.fixtures.main.sequence_run import SequenceRun
from tests.stories.fixtures.main.working_agent import WorkingAgent

FIRST_STEP = 1


@story(PausedSequenceRun, mode=BUILDER_MODE, subject=AgentRole.MAIN)
def test_a_paused_run_keeps_its_state_and_following_again_says_the_step(story):
    result = story.agent_runs(story.agents.subject, "sequence follow")
    result.expect_agent_told(story.agents.subject, SequencesNudges.CURRENT_STEP, n=story.sequences.first, step=FIRST_STEP)
    story.expect_stack(story.agents.subject, Ready, FollowingSequence)


@story(SequenceRun, mode=BUILDER_MODE, subject=AgentRole.MAIN)
def test_a_pause_with_no_reason_is_refused(story):
    story.agent_runs(story.agents.subject, "sequence follow")
    result = story.agent_runs(story.agents.subject, "sequence pause")
    result.expect_command_refused()
    result.expect_agent_not_told(story.agents.subject, SequencesNudges.SEQUENCE_PAUSED, n=story.sequences.first)
    story.expect_stack(story.agents.subject, Ready, FollowingSequence)


@story(SequenceRun, mode=BUILDER_MODE, subject=AgentRole.MAIN)
def test_an_abandon_names_the_steps_it_skips_and_waits_for_sure(story):
    story.agent_runs(story.agents.subject, "sequence follow")
    result = story.agent_runs(story.agents.subject, "sequence abandon --why 'the release moved to Friday'")
    result.expect_command_refused()
    result.expect_command_text("push the tag")
    result.expect_agent_not_told(story.agents.subject, SequencesNudges.SEQUENCE_ABANDONED, n=story.sequences.first)
    story.expect_stack(story.agents.subject, Ready, FollowingSequence)


@story(SequenceRun, mode=BUILDER_MODE, subject=AgentRole.MAIN)
def test_an_abandon_with_sure_ends_the_run_and_says_so(story):
    story.agent_runs(story.agents.subject, "sequence follow")
    result = story.agent_runs(story.agents.subject, "sequence abandon --why 'the release moved to Friday' --sure")
    result.expect_command_passed()
    result.expect_agent_told(story.agents.subject, SequencesNudges.SEQUENCE_ABANDONED, n=story.sequences.first)
    story.expect_stack(story.agents.subject, Ready)


@story(SequenceRun, mode=BUILDER_MODE, subject=AgentRole.MAIN)
def test_an_abandon_before_the_step_is_taken_up_is_refused(story):
    result = story.agent_runs(story.agents.subject, "sequence abandon --why 'the release moved to Friday' --sure")
    result.expect_command_refused()
    result.expect_agent_not_told(story.agents.subject, SequencesNudges.SEQUENCE_ABANDONED, n=story.sequences.first)
    story.expect_stack(story.agents.subject, Ready, FollowingSequence)


@story(SequenceRun, mode=BUILDER_MODE, subject=AgentRole.MAIN)
def test_an_abandoned_inner_sequence_gives_the_outer_back_with_its_step(story):
    inner = story.agent_creates_sequence(story.agents.subject, "tag", "push the tag | write the notes")
    story.agent_runs(story.agents.subject, f"sequence run {inner}")
    story.expect_stack(story.agents.subject, Ready, FollowingSequence, FollowingSequence)
    story.agent_runs(story.agents.subject, "sequence follow")
    result = story.agent_runs(story.agents.subject, "sequence abandon --why 'the tag waits for the review' --sure")
    result.expect_agent_told(story.agents.subject, SequencesNudges.SEQUENCE_ABANDONED, n=inner)
    result.expect_agent_told(story.agents.subject, SequencesNudges.PENDING_STEP, n=story.sequences.first, step=FIRST_STEP)
    story.expect_stack(story.agents.subject, Ready, FollowingSequence)


@story(WorkingAgent, mode=BUILDER_MODE, subject=AgentRole.MAIN)
def test_following_with_no_sequence_running_is_refused(story):
    result = story.agent_runs(story.agents.subject, "sequence follow")
    result.expect_command_refused()
    story.expect_stack(story.agents.subject, Ready)
