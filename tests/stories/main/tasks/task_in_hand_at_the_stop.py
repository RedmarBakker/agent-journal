from journal.features.tasks.states.ready import Ready
from journal.features.tasks.states.working import Working
from journal.features.tasks.tasks_nudges import TasksNudges
from journal.features.tasks.tasks_options import TasksOptions
from journal.models.task_state import TaskState
from journal.support.agent_role import AgentRole
from tests.stories.builder.story_marks import setting, story
from tests.stories.fixtures.main.started_task import StartedTask
from tests.stories.fixtures.main.working_agent import WorkingAgent


@story(StartedTask, subject=AgentRole.MAIN)
@setting(TasksOptions.LOG_AGE_LIMIT, 10)
def test_a_stop_after_the_log_age_limit_asks_for_a_log_first(story):
    story.time_travel(minutes=story.setting(TasksOptions.LOG_AGE_LIMIT) + 1)
    result = story.agent_stops(story.agents.subject)
    result.expect_refused(story.agents.subject, TasksNudges.STOP_LOG_REQUEST)
    story.agent_runs(story.agents.subject, f"task log {story.tasks.started} 'the footer has its links'")
    result = story.agent_stops(story.agents.subject)
    result.expect_refused(story.agents.subject, TasksNudges.TASK_CONTINUATION)
    story.expect_stack(story.agents.subject, Ready, Working)


@story(StartedTask, subject=AgentRole.MAIN)
@setting(TasksOptions.FIRST_DELAY, 2)
def test_a_stop_after_enough_edits_asks_for_a_log_first(story):
    story.repeat(int(story.setting(TasksOptions.FIRST_DELAY)), lambda: story.agent_writes(story.agents.subject, "a.py"))
    result = story.agent_stops(story.agents.subject)
    result.expect_refused(story.agents.subject, TasksNudges.STOP_LOG_REQUEST)
    story.expect_task(story.tasks.started, state=TaskState.STARTED)
    story.expect_stack(story.agents.subject, Ready, Working)


@story(StartedTask, subject=AgentRole.MAIN)
def test_a_completed_task_leaves_the_hand_and_the_stop_goes_through(story):
    story.agent_runs(story.agents.subject, f"task complete {story.tasks.started} --how done")
    result = story.agent_stops(story.agents.subject)
    result.expect_allowed()
    story.expect_stack(story.agents.subject, Ready)


@story(WorkingAgent, subject=AgentRole.MAIN)
def test_with_nothing_in_hand_and_nothing_open_the_stop_goes_through(story):
    result = story.agent_stops(story.agents.subject)
    result.expect_allowed()
    story.expect_stack(story.agents.subject, Ready)


@story(WorkingAgent, subject=AgentRole.MAIN)
@setting(TasksOptions.AUTO, False)
def test_an_open_task_without_auto_mode_lets_the_stop_go_through(story):
    task = story.agent_creates_task(story.agents.subject, "the header")
    result = story.agent_stops(story.agents.subject)
    result.expect_allowed()
    story.expect_task(task, state=TaskState.OPEN)
    story.expect_stack(story.agents.subject, Ready)


@story(StartedTask, subject=AgentRole.MAIN)
def test_a_new_session_start_names_the_task_in_hand(story):
    result = story.agent_starts_a_session(story.agents.subject)
    result.expect_agent_told(story.agents.subject, TasksNudges.TASK_CONTINUATION)
    story.expect_task(story.tasks.started, state=TaskState.STARTED)
    story.expect_stack(story.agents.subject, Ready, Working)
