from journal.engine.states.compacting import Compacting
from journal.features.briefing.briefing_nudges import BriefingNudges
from journal.features.tasks.states.ready import Ready
from journal.features.tasks.states.working import Working
from journal.features.tasks.tasks_nudges import TasksNudges
from journal.models.task_state import TaskState
from journal.support.agent_role import AgentRole
from tests.stories.builder.story_marks import story
from tests.stories.fixtures.main.compacting_task import CompactingTask


@story(CompactingTask, subject=AgentRole.MAIN)
def test_a_message_while_compacting_pushes_nothing_over_the_compaction(story):
    story.user_sends_message("is the footer done?")
    story.expect_task(story.tasks.started, state=TaskState.STARTED)
    story.expect_stack(story.agents.subject, Ready, Working, Compacting)


@story(CompactingTask, subject=AgentRole.MAIN)
def test_a_compaction_that_never_starts_again_is_dropped_by_the_next_tool_use(story):
    result = story.agent_reads(story.agents.subject)
    result.expect_allowed()
    result.expect_agent_not_told(story.agents.subject, BriefingNudges.OVERVIEW_FIRST)
    story.expect_task(story.tasks.started, state=TaskState.STARTED)
    story.expect_stack(story.agents.subject, Ready, Working)


@story(CompactingTask, subject=AgentRole.MAIN)
def test_a_prompt_while_compacting_ends_the_compaction(story):
    story.agent_is_prompted(story.agents.subject, "go on with the footer")
    result = story.agent_reads(story.agents.subject)
    result.expect_allowed()
    story.expect_task(story.tasks.started, state=TaskState.STARTED)
    story.expect_stack(story.agents.subject, Ready, Working)


@story(CompactingTask, subject=AgentRole.MAIN)
def test_a_stop_while_compacting_ends_it_and_the_task_in_hand_answers(story):
    result = story.agent_stops(story.agents.subject)
    result.expect_refused(story.agents.subject, TasksNudges.TASK_CONTINUATION)
    story.expect_task(story.tasks.started, state=TaskState.STARTED)
    story.expect_stack(story.agents.subject, Ready, Working)
