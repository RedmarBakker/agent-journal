from journal.engine.states.ended import Ended
from journal.features.briefing.briefing_nudges import BriefingNudges
from journal.features.tasks.states.ready import Ready
from journal.features.tasks.states.working import Working
from journal.models.task_state import TaskState
from journal.features.workers.workers_options import BUILDER_MODE
from journal.support.agent_role import AgentRole
from tests.stories.builder.story_marks import story
from tests.stories.fixtures.main.ended_task import EndedTask


@story(EndedTask, mode=BUILDER_MODE, subject=AgentRole.MAIN)
def test_a_second_session_end_stacks_no_second_ended(story):
    story.agent_ends_the_session(story.agents.subject)
    story.expect_task(story.tasks.started, state=TaskState.STARTED)
    story.expect_stack(story.agents.subject, Ready, Working, Ended)


@story(EndedTask, mode=BUILDER_MODE, subject=AgentRole.MAIN)
def test_a_tool_use_after_the_end_brings_the_work_back(story):
    story.agent_reads(story.agents.subject)
    story.expect_allowed()
    story.expect_agent_not_told(story.agents.subject, BriefingNudges.JOURNAL_READY)
    story.expect_stack(story.agents.subject, Ready, Working)


@story(EndedTask, mode=BUILDER_MODE, subject=AgentRole.MAIN)
def test_a_prompt_after_the_end_brings_the_work_back(story):
    story.agent_is_prompted(story.agents.subject, "go on with the footer")
    story.expect_agent_not_told(story.agents.subject, BriefingNudges.JOURNAL_READY)
    story.expect_task(story.tasks.started, state=TaskState.STARTED)
    story.expect_stack(story.agents.subject, Ready, Working)


@story(EndedTask, mode=BUILDER_MODE, subject=AgentRole.MAIN)
def test_a_session_start_after_the_end_brings_the_work_back_with_the_start_block(story):
    story.agent_starts_a_session(story.agents.subject)
    story.expect_agent_told(story.agents.subject, BriefingNudges.JOURNAL_READY)
    story.expect_agent_told(story.agents.subject, BriefingNudges.OVERVIEW_REQUEST)
    story.expect_stack(story.agents.subject, Ready, Working)


@story(EndedTask, mode=BUILDER_MODE, subject=AgentRole.MAIN)
def test_a_message_to_an_ended_agent_pushes_nothing_over_its_end(story):
    story.user_sends_message("is the footer done?")
    story.expect_task(story.tasks.started, state=TaskState.STARTED)
    story.expect_stack(story.agents.subject, Ready, Working, Ended)
