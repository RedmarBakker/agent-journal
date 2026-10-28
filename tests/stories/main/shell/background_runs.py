from journal.features.shell.shell_nudges import ShellNudges
from journal.features.shell.shell_options import ShellOptions
from journal.features.tasks.states.external_wait import ExternalWait
from journal.features.tasks.states.ready import Ready
from journal.features.tasks.states.working import Working
from journal.features.tasks.tasks_nudges import TasksNudges
from journal.features.workers.workers_options import BUILDER_MODE
from journal.models.task_state import TaskState
from journal.support.foreground_option import FOREGROUND_OPTION
from journal.support.agent_role import AgentRole
from tests.stories.builder.story_marks import setting, story
from tests.stories.fixtures.main.started_task import StartedTask
from tests.stories.fixtures.main.working_agent import WorkingAgent


@story(StartedTask, mode=BUILDER_MODE, scope=AgentRole.MAIN)
@setting(FOREGROUND_OPTION, 1)
def test_a_run_moved_to_the_background_holds_the_stop_until_the_agent_awaits_it_and_its_end_ends_the_wait(story):
    output = story.agent_runs_a_command(f"sleep {story.setting(FOREGROUND_OPTION) * 2}")
    story.expect_agent_told(ShellNudges.BACKGROUND_MOVE, n=output)
    story.agent_stops()
    story.expect_refused(ShellNudges.RUNNING_OUTPUT_STOP, outputs=output)
    story.agent_runs(f"await 'the sleep' --output {output}")
    story.agent_stops()
    story.expect_allowed()
    story.expect_stack(Ready, Working, ExternalWait)
    story.background_run_ends(output)
    story.expect_agent_told(TasksNudges.WAIT_END)
    story.expect_task(story.start.started_task, state=TaskState.STARTED)
    story.expect_stack(Ready, Working)


@story(WorkingAgent, mode=BUILDER_MODE, scope=AgentRole.MAIN)
@setting(ShellOptions.MESSAGE_FOREGROUND_LIMIT, 1)
def test_a_message_waiting_for_the_agent_moves_a_run_sooner(story):
    story.user_sends_message("how far is the footer?")
    output = story.agent_runs_a_command(f"sleep {story.setting(ShellOptions.MESSAGE_FOREGROUND_LIMIT) * 2}")
    story.expect_agent_told(ShellNudges.BACKGROUND_MOVE, n=output)
    story.expect_stack(Ready)


@story(WorkingAgent, mode=BUILDER_MODE, scope=AgentRole.MAIN)
def test_a_test_run_moves_to_the_background_at_once_and_is_watched(story):
    output = story.agent_runs_a_command("pytest -q --co")
    story.expect_agent_told(ShellNudges.WATCH_VIEW, n=output)
    story.expect_stack(Ready)
