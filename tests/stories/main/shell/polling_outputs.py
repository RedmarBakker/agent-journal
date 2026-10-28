from journal.features.tasks.states.ready import Ready
from journal.features.tasks.states.working import Working
from journal.features.tasks.tasks_conduct import POLL_REPEAT_COMMANDS
from journal.features.tasks.tasks_nudges import TasksNudges
from journal.features.workers.workers_options import BUILDER_MODE
from journal.models.task_state import TaskState
from journal.support.foreground_option import FOREGROUND_OPTION
from tests.stories.builder.story_marks import setting, story
from tests.stories.fixtures.main.started_task import StartedTask
from tests.stories.fixtures.main.working_agent import WorkingAgent


@story(WorkingAgent, mode=BUILDER_MODE)
def test_the_third_poll_in_a_row_of_the_same_output_is_refused_with_the_await(story):
    output = story.agent_runs_a_command("echo hi | head -1")
    story.agent_runs_in_the_shell(f"journal output status {output}")
    story.agent_runs_in_the_shell(f"journal output status {output}")
    story.expect_allowed()
    story.agent_runs_in_the_shell(f"journal output status {output}")
    story.expect_refused(TasksNudges.OUTPUT_POLL_REFUSAL, n=output)
    story.expect_stack(Ready)


@story(WorkingAgent, mode=BUILDER_MODE)
def test_a_poll_of_another_output_between_is_no_repeat(story):
    first = story.agent_runs_a_command("echo hi | head -1")
    second = story.agent_runs_a_command("echo ho | head -1")
    story.agent_runs_in_the_shell(f"journal output status {first}")
    story.agent_runs_in_the_shell(f"journal output status {second}")
    story.agent_runs_in_the_shell(f"journal output status {first}")
    story.expect_allowed()
    story.expect_stack(Ready)


@story(WorkingAgent, mode=BUILDER_MODE)
def test_the_same_command_run_again_and_again_is_named(story):
    for _ in range(POLL_REPEAT_COMMANDS):
        story.agent_runs_in_the_shell("git status")
    story.expect_agent_told(TasksNudges.STOP_POLLING, times=POLL_REPEAT_COMMANDS, command="git status")
    story.expect_stack(Ready)


@story(StartedTask, mode=BUILDER_MODE)
@setting(FOREGROUND_OPTION, 1)
def test_a_wait_on_a_background_run_ends_when_the_run_ends(story):
    output = story.agent_runs_a_command(f"sleep {story.setting(FOREGROUND_OPTION) * 2}")
    story.agent_runs(f"await 'the sleep' --output {output}")
    story.background_run_ends(output)
    story.expect_agent_told(TasksNudges.WAIT_END)
    story.expect_task(story.start.started_task, state=TaskState.STARTED)
    story.expect_stack(Ready, Working)
