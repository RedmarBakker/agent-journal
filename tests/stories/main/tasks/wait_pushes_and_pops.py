from journal.features.tasks.states.external_wait import ExternalWait
from journal.features.tasks.states.ready import Ready
from journal.features.tasks.states.working import Working
from journal.features.tasks.tasks_nudges import TasksNudges
from journal.models.task_state import TaskState
from journal.support.agent_role import AgentRole
from tests.stories.builder.story_marks import story
from tests.stories.fixtures.main.build_wait import BuildWait
from tests.stories.fixtures.main.started_task import StartedTask


@story(BuildWait, subject=AgentRole.MAIN)
def test_a_wait_with_a_task_in_progress_lets_the_stop_go_through(story):
    result = story.agent_stops(story.agents.subject)
    result.expect_allowed()
    story.expect_task(story.tasks.started, state=TaskState.STARTED)
    story.expect_stack(story.agents.subject, Ready, Working, ExternalWait)


@story(BuildWait, subject=AgentRole.MAIN)
def test_a_task_started_during_a_wait_is_carried_on_with_once(story):
    story.agent_runs(story.agents.subject, f"task test {story.tasks.started}")
    result = story.agent_stops(story.agents.subject)
    result.expect_refused(story.agents.subject, TasksNudges.WAIT_NEXT_TASK, n=story.tasks.open)
    result = story.agent_stops(story.agents.subject)
    result.expect_allowed()
    story.expect_stack(story.agents.subject, Ready, Working, ExternalWait)


@story(StartedTask, subject=AgentRole.MAIN)
def test_working_again_ends_the_wait(story):
    story.agent_runs(story.agents.subject, "await 'the build' --until false")
    story.agent_writes(story.agents.subject, "a.py")
    story.expect_task(story.tasks.started, state=TaskState.STARTED)
    story.expect_stack(story.agents.subject, Ready, Working)


@story(StartedTask, subject=AgentRole.MAIN)
def test_a_wait_that_names_nothing_to_wait_on_is_refused(story):
    result = story.agent_runs(story.agents.subject, "await 'the build'")
    result.expect_command_refused()
    story.expect_task(story.tasks.started, state=TaskState.STARTED)
    story.expect_stack(story.agents.subject, Ready, Working)
