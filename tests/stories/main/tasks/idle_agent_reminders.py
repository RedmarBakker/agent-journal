from journal.support.timeout import Timeout
from journal.features.tasks.states.ready import IDLE_CHECK_DELAY_SECONDS, Ready
from journal.features.tasks.tasks_nudges import TasksNudges
from journal.models.task_state import TaskState
from journal.support.agent_role import AgentRole
from tests.stories.builder.story_marks import story
from tests.stories.fixtures.main.ready_after_new_session import ReadyAfterNewSession
from tests.stories.fixtures.main.working_agent import WorkingAgent


@story(ReadyAfterNewSession, subject=AgentRole.MAIN)
def test_a_new_session_with_open_work_gets_no_idle_line_after_a_minute(story):
    task = story.user_posted("/journal/tasks", {"title": "the header"})["id"]
    result = story.agent_is_quiet_past(story.agents.subject, Timeout.minutes(1).amount)
    result.expect_agent_not_told(story.agents.subject, TasksNudges.IDLE_CHECK)
    story.expect_task(task, state=TaskState.OPEN)
    story.expect_stack(story.agents.subject, Ready)


@story(ReadyAfterNewSession, subject=AgentRole.MAIN)
def test_a_new_session_with_open_work_gets_the_idle_line_after_half_an_hour(story):
    task = story.user_posted("/journal/tasks", {"title": "the header"})["id"]
    result = story.agent_is_quiet_past(story.agents.subject, IDLE_CHECK_DELAY_SECONDS)
    result.expect_agent_told(story.agents.subject, TasksNudges.IDLE_CHECK)
    story.expect_task(task, state=TaskState.OPEN)
    story.expect_stack(story.agents.subject, Ready)


@story(WorkingAgent, subject=AgentRole.MAIN)
def test_half_an_hour_of_nothing_with_no_work_says_nothing(story):
    result = story.agent_is_quiet_past(story.agents.subject, IDLE_CHECK_DELAY_SECONDS)
    result.expect_agent_not_told(story.agents.subject, TasksNudges.IDLE_CHECK)
    story.expect_stack(story.agents.subject, Ready)
