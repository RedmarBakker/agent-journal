from journal.features.briefing.briefing_nudges import BriefingNudges
from journal.features.tasks.states.ready import Ready
from journal.features.tasks.states.working import Working
from journal.models.task_state import TaskState
from journal.features.workers.workers_options import BUILDER_MODE
from journal.support.agent_role import AgentRole
from tests.stories.builder.story_marks import story
from tests.stories.fixtures.main.task_queue import TaskQueue
from tests.stories.fixtures.main.working_agent import WorkingAgent


@story(WorkingAgent, mode=BUILDER_MODE, scope=AgentRole.MAIN)
def test_a_start_says_the_journal_is_ready_how_to_handle_it_the_laws_and_asks_for_the_overview(story):
    story.agent_starts_a_session()
    story.expect_agent_told(BriefingNudges.JOURNAL_READY)
    story.expect_agent_told(BriefingNudges.JOURNAL_DISCRETION)
    story.expect_agent_told(BriefingNudges.JOURNAL_LAWS)
    story.expect_agent_told(BriefingNudges.OVERVIEW_REQUEST)
    story.expect_stack(Ready)


@story(TaskQueue, mode=BUILDER_MODE, scope=AgentRole.MAIN)
def test_a_start_lists_what_waits_for_the_agent(story):
    story.user_sends_message("is the footer done?")
    story.agent_starts_a_session()
    story.expect_agent_told(BriefingNudges.PENDING_ITEMS)
    story.expect_task(story.start.next_open, state=TaskState.OPEN)
    story.expect_stack(Ready, Working)
