from journal.features.sequences.sequences_nudges import SequencesNudges
from journal.features.sequences.states.following_sequence import FollowingSequence
from journal.features.tasks.states.ready import Ready
from journal.features.workers.workers_options import BUILDER_MODE
from journal.support.agent_role import AgentRole
from tests.stories.builder.story_marks import story
from tests.stories.fixtures.main.paused_sequence_run import PausedSequenceRun
from tests.stories.fixtures.main.sequence_run import SequenceRun

FIRST_STEP = 1


@story(SequenceRun, mode=BUILDER_MODE, scope=AgentRole.MAIN)
def test_a_new_session_takes_the_run_over_with_its_step_and_follows_it_to_the_end(story):
    story.second_session_starts()
    story.expect_agent_told(SequencesNudges.PENDING_STEP, n=story.start.sequence, step=FIRST_STEP)
    story.expect_stack(Ready, FollowingSequence)
    story.agent_looks_at_the_overview()
    story.agent_runs("sequence follow")
    story.agent_runs("sequence next")
    story.agent_runs("sequence follow")
    story.agent_runs("sequence next")
    story.expect_agent_told(SequencesNudges.SEQUENCE_ENDED, n=story.start.sequence)
    story.expect_stack(Ready)


@story(PausedSequenceRun, mode=BUILDER_MODE, scope=AgentRole.MAIN)
def test_a_paused_run_arrives_paused_in_the_new_session_and_says_so(story):
    story.second_session_starts()
    story.expect_agent_told(SequencesNudges.SEQUENCE_PAUSED, n=story.start.sequence)
    story.expect_stack(Ready, FollowingSequence)
