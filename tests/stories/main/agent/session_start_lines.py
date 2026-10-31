from journal.features.briefing.briefing_nudges import BriefingNudges
from journal.features.tasks.states.ready import Ready
from journal.features.tasks.states.working import Working
from journal.features.tasks.tasks_nudges import TasksNudges
from journal.features.voices.voices_nudges import VoicesNudges
from journal.models.task_state import TaskState
from journal.features.workers.workers_options import BUILDER_MODE
from journal.support.agent_role import AgentRole
from tests.stories.builder.story_marks import story
from tests.stories.fixtures.main.session_opening import SessionOpening
from tests.stories.fixtures.main.task_queue import TaskQueue
from tests.stories.fixtures.main.working_agent import WorkingAgent


@story(WorkingAgent, mode=BUILDER_MODE, subject=AgentRole.MAIN)
def test_a_start_says_the_journal_is_ready_how_to_handle_it_the_laws_and_asks_for_the_overview(story):
    result = story.agent_starts_a_session(story.agents.subject)
    result.expect_agent_told(story.agents.subject, BriefingNudges.JOURNAL_READY)
    result.expect_agent_told(story.agents.subject, BriefingNudges.JOURNAL_DISCRETION)
    result.expect_agent_told(story.agents.subject, BriefingNudges.JOURNAL_LAWS)
    result.expect_agent_told(story.agents.subject, BriefingNudges.OVERVIEW_REQUEST)
    story.expect_stack(story.agents.subject, Ready)


@story(TaskQueue, mode=BUILDER_MODE, subject=AgentRole.MAIN)
def test_a_start_lists_what_waits_for_the_agent(story):
    story.user_sends_message("is the footer done?")
    result = story.agent_starts_a_session(story.agents.subject)
    result.expect_agent_told(story.agents.subject, BriefingNudges.PENDING_ITEMS)
    story.expect_task(story.tasks.open, state=TaskState.OPEN)
    story.expect_stack(story.agents.subject, Ready, Working)


@story(WorkingAgent, mode=BUILDER_MODE, subject=AgentRole.MAIN)
def test_a_session_start_does_not_name_a_missing_task_as_in_hand(story):
    result = story.agent_runs(story.agents.subject, "panic working task_id=1")
    result.expect_command_passed()
    result = story.agent_starts_a_session(story.agents.subject)
    result.expect_agent_not_told(story.agents.subject, TasksNudges.TASK_CONTINUATION)
    story.expect_stack(story.agents.subject, Ready)


@story(SessionOpening, mode=BUILDER_MODE, subject=AgentRole.MAIN)
def test_a_new_session_asks_for_an_introduction_after_the_start_skills_are_read(story):
    story.last_step.expect_agent_not_told(story.agents.subject, VoicesNudges.INTRODUCE_YOURSELF)
    story.agent_reads_a_skill(story.agents.subject, "journal")
    story.agent_reads_a_skill(story.agents.subject, "journal-etiquette")
    result = story.agent_reads_a_skill(story.agents.subject, "journal-messages")
    result.expect_agent_told(story.agents.subject, VoicesNudges.INTRODUCE_YOURSELF)
    story.expect_stack(story.agents.subject, Ready)
