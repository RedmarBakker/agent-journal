from journal.features.tasks.states.ready import Ready
from journal.features.tasks.states.working import Working
from journal.features.tasks.tasks_nudges import TasksNudges
from journal.features.tasks.tasks_options import TasksOptions
from journal.models.task_state import TaskState
from journal.features.workers.workers_options import BUILDER_MODE
from journal.support.agent_role import AgentRole
from tests.stories.builder.story_marks import setting, story
from tests.stories.fixtures.main.started_task import StartedTask
from tests.stories.fixtures.main.testing_task import TestingTask


@story(StartedTask, mode=BUILDER_MODE, scope=AgentRole.MAIN)
@setting(TasksOptions.TESTING_SUGGESTION_MINUTES, 0)
@setting(TasksOptions.TESTING_SUGGESTION_TOOL_USES, 3)
def test_a_test_run_on_a_long_task_suggests_putting_it_in_testing(story):
    story.agent_runs_in_the_shell("pytest -q")
    story.expect_agent_not_told(TasksNudges.TESTING_SUGGESTION)
    story.agent_reads()
    story.agent_runs_in_the_shell("pytest -q")
    story.expect_agent_told(TasksNudges.TESTING_SUGGESTION, n=story.start.started_task)
    story.expect_stack(Ready, Working)


@story(TestingTask, mode=BUILDER_MODE, scope=AgentRole.MAIN)
def test_a_task_in_testing_is_completed_when_its_run_passes(story):
    run = story.agent_runs_a_command("sh -c 'seq 1 300; exit 0'")
    story.agent_runs(f"output test {run}")
    story.expect_task(story.start.started_task, state=TaskState.COMPLETED)
    story.expect_stack(Ready)


@story(TestingTask, mode=BUILDER_MODE, scope=AgentRole.MAIN)
def test_a_task_in_testing_is_paused_when_its_run_fails(story):
    run = story.agent_runs_a_command("sh -c 'seq 1 300; exit 3'")
    story.agent_runs(f"output test {run}")
    story.expect_task(story.start.started_task, state=TaskState.PAUSED)
    story.expect_agent_told(TasksNudges.TEST_FAILURE, n=story.start.started_task)
    story.expect_stack(Ready)
