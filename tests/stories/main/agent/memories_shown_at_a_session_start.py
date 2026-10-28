from journal.features.briefing.briefing_nudges import BriefingNudges
from journal.features.tasks.states.ready import Ready
from journal.features.tasks.states.working import Working
from journal.models.memory import HEAVIEST
from journal.models.task_state import TaskState
from journal.features.workers.workers_options import BUILDER_MODE
from journal.support.agent_role import AgentRole
from tests.stories.builder.story_marks import story
from tests.stories.fixtures.main.compacted_memories import CompactedMemories
from tests.stories.fixtures.main.context_mark_task import ContextMarkTask
from tests.stories.fixtures.main.working_agent import WorkingAgent


@story(ContextMarkTask, mode=BUILDER_MODE, scope=AgentRole.MAIN)
def test_a_memory_added_at_the_mark_is_shown_at_the_next_session_start(story):
    story.agent_adds_memory("the footer links go in a list", HEAVIEST)
    story.agent_starts_a_session()
    story.expect_agent_told(BriefingNudges.ENVIRONMENT_MEMORIES)
    story.expect_task(story.start.started_task, state=TaskState.STARTED)
    story.expect_stack(Ready, Working)


@story(WorkingAgent, mode=BUILDER_MODE, scope=AgentRole.MAIN)
def test_a_reminder_is_shown_at_the_next_session_start(story):
    story.agent_runs("reminder create 'check the footer on a phone'")
    story.agent_starts_a_session()
    story.expect_agent_told(BriefingNudges.ENVIRONMENT_REMINDERS)
    story.expect_stack(Ready)


@story(CompactedMemories, mode=BUILDER_MODE, scope=AgentRole.MAIN)
def test_a_memory_that_faded_out_is_not_shown_again_and_a_heavier_one_is(story):
    story.agent_looks_at_the_overview()
    story.agent_starts_a_session()
    story.expect_agent_told(BriefingNudges.ENVIRONMENT_MEMORIES)
    story.expect_row_absent("memories", story.start.light_memory)
    story.expect_row("memories", story.start.heavy_memory, {"weight": HEAVIEST - 1})
    story.expect_stack(Ready)
