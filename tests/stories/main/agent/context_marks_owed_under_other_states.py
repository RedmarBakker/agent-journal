from journal.features.briefing.briefing_nudges import BriefingNudges
from journal.features.briefing.states.reading_overview import ReadingOverview
from journal.features.memory.memory_nudges import MemoryNudges
from journal.features.memory.memory_thresholds import MemoryThresholds
from journal.features.memory.states.weighing_memories import WeighingMemories
from journal.features.plans.states.following_plan import FollowingPlan
from journal.features.sequences.sequences_nudges import SequencesNudges
from journal.features.sequences.states.following_sequence import FollowingSequence
from journal.features.tasks.states.ready import Ready
from journal.features.tasks.states.working import Working
from journal.models.task_state import TaskState
from journal.features.workers.workers_options import BUILDER_MODE
from tests.stories.builder.story_marks import story
from tests.stories.fixtures.main.build_wait import BuildWait
from tests.stories.fixtures.main.compacted_task import CompactedTask
from tests.stories.fixtures.main.context_mark_sequence import ContextMarkSequence
from tests.stories.fixtures.main.started_plan import StartedPlan

FIRST = MemoryThresholds.CONTEXT[0]


@story(CompactedTask, mode=BUILDER_MODE)
def test_a_mark_reached_while_the_overview_is_owed_is_asked_once_the_overview_is_read(story):
    story.context_reaches(FIRST)
    story.agent_reads()
    story.expect_refused(BriefingNudges.OVERVIEW_FIRST)
    story.expect_stack(Ready, Working, ReadingOverview)
    story.agent_looks_at_the_overview()
    story.agent_reads()
    story.expect_agent_told(MemoryNudges.CONTEXT_DECISION, percent=FIRST)
    story.expect_stack(Ready, Working, WeighingMemories)


@story(BuildWait, mode=BUILDER_MODE)
def test_a_mark_reached_while_the_agent_waits_is_asked_when_it_works_again(story):
    story.agent_consumes_context(FIRST)
    story.expect_agent_told(MemoryNudges.CONTEXT_DECISION, percent=FIRST)
    story.expect_task(story.start.started_task, state=TaskState.STARTED)
    story.expect_stack(Ready, Working, WeighingMemories)


@story(StartedPlan, mode=BUILDER_MODE)
def test_a_mark_reached_in_a_followed_plan_is_weighed_on_top_of_the_plan(story):
    story.agent_consumes_context(FIRST)
    story.expect_stack(Ready, FollowingPlan, WeighingMemories)
    story.agent_runs("memory skip 'nothing new to keep'")
    story.expect_task(story.start.first_task, state=TaskState.STARTED)
    story.expect_stack(Ready, FollowingPlan)


@story(ContextMarkSequence, mode=BUILDER_MODE)
def test_a_mark_reached_in_a_running_sequence_holds_writes_for_the_memories_then_says_the_step_again(story):
    story.agent_writes("footer.py")
    story.expect_refused(MemoryNudges.DECISION_EDIT_BLOCK)
    story.agent_runs("memory skip 'nothing new to keep'")
    story.expect_agent_told(SequencesNudges.PENDING_STEP, n=story.start.sequence, step=1)
    story.expect_stack(Ready, FollowingSequence)


@story(ContextMarkSequence, mode=BUILDER_MODE)
def test_a_stop_at_the_mark_inside_a_sequence_is_held_by_the_memories_first(story):
    story.agent_stops()
    story.expect_refused(MemoryNudges.UNDECIDED_STOP, percent=FIRST)
    story.expect_agent_not_told(SequencesNudges.PENDING_STEP)
    story.expect_row("sequences", story.start.sequence, {})
    story.expect_stack(Ready, FollowingSequence, WeighingMemories)
