from journal.features.sequences.sequences_nudges import SequencesNudges
from journal.features.sequences.sequences_options import SequencesOptions
from journal.features.questions.states.waiting import Waiting
from journal.features.sequences.states.following_sequence import FollowingSequence
from journal.features.tasks.states.ready import Ready
from journal.features.workers.workers_options import BUILDER_MODE
from journal.support.agent_role import AgentRole
from tests.stories.builder.story_marks import setting, story
from tests.stories.fixtures.main.paused_sequence_run import PausedSequenceRun
from tests.stories.fixtures.main.sequence_run import SequenceRun

FIRST_STEP = 1


@story(SequenceRun, mode=BUILDER_MODE, subject=AgentRole.MAIN)
def test_a_stop_after_a_tool_use_with_the_step_open_is_refused_with_the_step(story):
    story.agent_reads(story.agents.subject)
    result = story.agent_stops(story.agents.subject)
    result.expect_refused(story.agents.subject, SequencesNudges.PENDING_STEP, n=story.sequences.first, step=FIRST_STEP)
    story.expect_stack(story.agents.subject, Ready, FollowingSequence)


@story(SequenceRun, mode=BUILDER_MODE, subject=AgentRole.MAIN)
def test_a_stop_right_after_the_step_was_said_goes_through(story):
    result = story.agent_stops(story.agents.subject)
    result.expect_allowed()
    result.expect_agent_not_told(story.agents.subject, SequencesNudges.PENDING_STEP, n=story.sequences.first)
    story.expect_stack(story.agents.subject, Ready, FollowingSequence)


@story(PausedSequenceRun, mode=BUILDER_MODE, subject=AgentRole.MAIN)
def test_a_paused_run_may_stop(story):
    result = story.agent_stops(story.agents.subject)
    result.expect_allowed()
    result.expect_agent_not_told(story.agents.subject, SequencesNudges.PENDING_STEP, n=story.sequences.first)
    story.expect_stack(story.agents.subject, Ready, FollowingSequence)


@story(SequenceRun, mode=BUILDER_MODE, subject=AgentRole.MAIN)
def test_an_open_question_to_the_user_lets_the_agent_stop(story):
    story.agent_runs(story.agents.subject, "sequence follow")
    story.agent_asks(story.agents.subject, "which version comes next?", "the agent raises the minor", "the agent raises the patch")
    result = story.agent_stops(story.agents.subject)
    result.expect_allowed()
    result.expect_agent_not_told(story.agents.subject, SequencesNudges.PENDING_STEP, n=story.sequences.first)
    story.expect_stack(story.agents.subject, Ready, FollowingSequence, Waiting)


@story(SequenceRun, mode=BUILDER_MODE, subject=AgentRole.MAIN)
@setting(SequencesOptions.STEP_REPEAT_INTERVAL, 10)
def test_a_quiet_agent_is_sent_the_step_again_after_the_set_minutes(story):
    result = story.agent_is_quiet_for(story.agents.subject, minutes=story.setting(SequencesOptions.STEP_REPEAT_INTERVAL) + 1)
    result.expect_agent_told(story.agents.subject, SequencesNudges.PENDING_STEP, n=story.sequences.first, step=FIRST_STEP)
    story.expect_stack(story.agents.subject, Ready, FollowingSequence)


@story(SequenceRun, mode=BUILDER_MODE, subject=AgentRole.MAIN)
@setting(SequencesOptions.STEP_REPEAT_INTERVAL, 10)
def test_a_quiet_agent_is_not_sent_the_step_before_the_set_minutes(story):
    result = story.agent_is_quiet_for(story.agents.subject, minutes=story.setting(SequencesOptions.STEP_REPEAT_INTERVAL) - 1)
    result.expect_agent_not_told(story.agents.subject, SequencesNudges.PENDING_STEP, n=story.sequences.first)
    story.expect_stack(story.agents.subject, Ready, FollowingSequence)
