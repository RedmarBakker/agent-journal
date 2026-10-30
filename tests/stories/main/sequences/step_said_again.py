from journal.features.briefing.states.reading_overview import ReadingOverview
from journal.features.sequences.sequences_nudges import SequencesNudges
from journal.features.sequences.states.following_sequence import FollowingSequence
from journal.features.tasks.states.ready import Ready
from journal.features.workers.workers_options import BUILDER_MODE
from journal.support.agent_role import AgentRole
from tests.stories.builder.story_marks import story
from tests.stories.fixtures.main.sequence_run import SequenceRun

FIRST_STEP = 1


@story(SequenceRun, mode=BUILDER_MODE, subject=AgentRole.MAIN)
def test_the_step_is_told_at_the_start_after_a_compaction(story):
    story.context_is_compacted()
    story.expect_agent_told(story.agents.subject, SequencesNudges.PENDING_STEP, n=story.sequences.first, step=FIRST_STEP)
    story.expect_stack(story.agents.subject, Ready, FollowingSequence, ReadingOverview)


@story(SequenceRun, mode=BUILDER_MODE, subject=AgentRole.MAIN)
def test_a_wait_that_ends_says_the_step_as_the_sequence_comes_back_on_top(story):
    story.agent_runs(story.agents.subject, "await 'the build' --until false")
    story.agent_reads(story.agents.subject)
    story.expect_agent_told(story.agents.subject, SequencesNudges.PENDING_STEP, n=story.sequences.first, step=FIRST_STEP)
    story.expect_stack(story.agents.subject, Ready, FollowingSequence)
