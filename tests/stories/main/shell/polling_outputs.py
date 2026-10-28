from journal.features.tasks.states.ready import Ready
from journal.features.tasks.states.working import Working
from journal.features.tasks.tasks_conduct import POLL_REPEAT_COMMANDS
from journal.features.tasks.tasks_nudges import TasksNudges
from journal.features.workers.workers_options import BUILDER_MODE
from journal.models.task_state import TaskState
from journal.support.foreground_option import FOREGROUND_OPTION
from journal.support.agent_role import AgentRole
from tests.stories.builder.story_marks import setting, story
from tests.stories.fixtures.main.started_task import StartedTask
from tests.stories.fixtures.main.working_agent import WorkingAgent


@story(WorkingAgent, mode=BUILDER_MODE, scope=AgentRole.MAIN)
def test_the_third_poll_in_a_row_of_the_same_output_is_refused_with_the_await(story):
    output = story.agent_runs_a_command("echo hi | head -1")
    story.agent_runs_in_the_shell(f"journal output status {output}")
    story.agent_runs_in_the_shell(f"journal output status {output}")
    story.expect_allowed()
    story.agent_runs_in_the_shell(f"journal output status {output}")
    story.expect_refused(TasksNudges.OUTPUT_POLL_REFUSAL, n=output)
    story.expect_stack(Ready)


@story(WorkingAgent, mode=BUILDER_MODE, scope=AgentRole.MAIN)
def test_the_same_command_run_again_and_again_is_named(story):
    for _ in range(POLL_REPEAT_COMMANDS):
        story.agent_runs_in_the_shell("git status")
    story.expect_agent_told(TasksNudges.STOP_POLLING, times=POLL_REPEAT_COMMANDS, command="git status")
    story.expect_stack(Ready)
