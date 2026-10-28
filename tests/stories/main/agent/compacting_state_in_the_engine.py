from journal.engine.states.compacting import Compacting
from journal.features.briefing.briefing_nudges import BriefingNudges
from journal.features.tasks.states.ready import Ready
from journal.features.tasks.states.working import Working
from journal.features.tasks.tasks_nudges import TasksNudges
from journal.models.task_state import TaskState
from journal.features.workers.workers_options import BUILDER_MODE
from tests.stories.builder.story_marks import story
from tests.stories.fixtures.main.compacting_task import CompactingTask


@story(CompactingTask, mode=BUILDER_MODE)
def test_a_message_while_compacting_pushes_nothing_over_the_compaction(story):
    story.user_sends_message("is the footer done?")
    story.expect_task(story.start.started_task, state=TaskState.STARTED)
    story.expect_stack(Ready, Working, Compacting)


@story(CompactingTask, mode=BUILDER_MODE)
def test_a_compaction_that_never_starts_again_is_dropped_by_the_next_tool_use(story):
    story.agent_reads()
    story.expect_allowed()
    story.expect_agent_not_told(BriefingNudges.OVERVIEW_FIRST)
    story.expect_task(story.start.started_task, state=TaskState.STARTED)
    story.expect_stack(Ready, Working)


@story(CompactingTask, mode=BUILDER_MODE)
def test_a_prompt_while_compacting_ends_the_compaction(story):
    story.agent_is_prompted("go on with the footer")
    story.agent_reads()
    story.expect_allowed()
    story.expect_task(story.start.started_task, state=TaskState.STARTED)
    story.expect_stack(Ready, Working)


@story(CompactingTask, mode=BUILDER_MODE)
def test_a_stop_while_compacting_ends_it_and_the_task_in_hand_answers(story):
    story.agent_stops()
    story.expect_refused(TasksNudges.TASK_CONTINUATION)
    story.expect_task(story.start.started_task, state=TaskState.STARTED)
    story.expect_stack(Ready, Working)
