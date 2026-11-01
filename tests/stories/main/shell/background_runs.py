from journal.features.shell.shell_nudges import ShellNudges
from journal.features.shell.shell_options import ShellOptions
from journal.features.tasks.states.external_wait import ExternalWait
from journal.features.tasks.states.ready import Ready
from journal.features.tasks.states.working import Working
from journal.features.tasks.tasks_nudges import TasksNudges
from journal.models.task_state import TaskState
from journal.support.agent_role import AgentRole
from tests.stories.builder.story_marks import setting, story
from tests.stories.fixtures.main.started_task import StartedTask
from tests.stories.fixtures.main.working_agent import WorkingAgent


@story(StartedTask, subject=AgentRole.MAIN)
def test_a_run_moved_to_the_background_holds_the_stop_until_the_agent_awaits_it_and_its_end_ends_the_wait(story):
    output = story.agent_has_a_background_run_printing(story.agents.subject, "sleep 2")
    story.last_step.expect_agent_told(story.agents.subject, ShellNudges.BACKGROUND_MOVE, n=output)
    result = story.agent_stops(story.agents.subject)
    result.expect_refused(story.agents.subject, ShellNudges.OPEN_OUTPUT_STOP, outputs=output)
    story.agent_runs(story.agents.subject, f"await 'the sleep' --output {output}")
    result = story.agent_stops(story.agents.subject)
    result.expect_allowed()
    story.expect_stack(story.agents.subject, Ready, Working, ExternalWait)
    result = story.background_run_ends(story.agents.subject, output)
    result.expect_agent_told(story.agents.subject, TasksNudges.WAIT_END)
    story.expect_task(story.tasks.started, state=TaskState.STARTED)
    story.expect_stack(story.agents.subject, Ready, Working)


@story(WorkingAgent, subject=AgentRole.MAIN)
@setting(ShellOptions.MESSAGE_FOREGROUND_LIMIT, 1)
def test_a_message_waiting_for_the_agent_moves_a_run_sooner(story):
    story.user_sends_message("how far is the footer?")
    output = story.agent_runs_a_command(story.agents.subject, f"sleep {story.setting(ShellOptions.MESSAGE_FOREGROUND_LIMIT) * 2}")
    story.last_step.expect_agent_told(story.agents.subject, ShellNudges.BACKGROUND_MOVE, n=output)
    story.expect_stack(story.agents.subject, Ready)


@story(WorkingAgent, subject=AgentRole.MAIN)
def test_a_test_run_moves_to_the_background_at_once_and_is_watched(story):
    output = story.agent_runs_a_command(story.agents.subject, "pytest -q --co")
    story.last_step.expect_agent_told(story.agents.subject, ShellNudges.WATCH_VIEW, n=output)
    story.expect_stack(story.agents.subject, Ready)


@story(WorkingAgent, subject=AgentRole.MAIN)
def test_a_shell_call_the_agent_would_run_in_its_own_background_runs_in_the_foreground_through_the_journal(story):
    result = story.agent_runs_in_its_own_background(story.agents.subject, "./scripts/test.sh")
    result.expect_allowed()
    result.expect_tool_input_changed(command="./scripts/test.sh", run_in_background=False)
    story.expect_stack(story.agents.subject, Ready)
