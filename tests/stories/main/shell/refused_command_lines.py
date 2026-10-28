from journal.features.messages.messages_nudges import MessagesNudges
from journal.features.shell.shell_nudges import ShellNudges
from journal.features.tasks.states.ready import Ready
from journal.features.tasks.states.working import Working
from journal.models.task_state import TaskState
from journal.features.workers.workers_options import BUILDER_MODE
from journal.support.agent_role import AgentRole
from tests.stories.builder.mode_floor import ModeFloor
from tests.stories.builder.story_marks import ALL_MODES, story
from tests.stories.fixtures.main.started_task import StartedTask
from tests.stories.fixtures.main.working_agent import WorkingAgent


@story(WorkingAgent, mode=ALL_MODES, scope=AgentRole.MAIN)
def test_a_journal_command_chained_before_another_is_refused_in_every_mode(story):
    story.agent_runs_in_the_shell("journal task list && ls")
    story.expect_refused(ShellNudges.JOURNAL_COMMAND_ISOLATION)
    story.expect_stack(ModeFloor)


@story(WorkingAgent, mode=BUILDER_MODE, scope=AgentRole.MAIN)
def test_a_journal_command_chained_after_another_is_refused(story):
    story.agent_runs_in_the_shell("ls; journal task list")
    story.expect_refused(ShellNudges.JOURNAL_COMMAND_ISOLATION)
    story.expect_stack(Ready)


@story(WorkingAgent, mode=BUILDER_MODE, scope=AgentRole.MAIN)
def test_a_message_read_piped_into_a_filter_is_refused(story):
    story.agent_runs_in_the_shell("journal message read 4 | head -3")
    story.expect_refused(MessagesNudges.FULL_MESSAGE_READ)
    story.expect_stack(Ready)


@story(WorkingAgent, mode=BUILDER_MODE, scope=AgentRole.MAIN)
def test_a_journal_command_read_whole_piped_into_a_filter_is_refused(story):
    story.agent_runs_in_the_shell("journal task show 4 | head -3")
    story.expect_refused(ShellNudges.PIPED_JOURNAL_COMMAND, command="task show", filter="head")
    story.expect_stack(Ready)


@story(WorkingAgent, mode=BUILDER_MODE, scope=AgentRole.MAIN)
def test_a_test_run_piped_into_a_filter_is_refused(story):
    story.agent_runs_in_the_shell("pytest -q | tail -5")
    story.expect_refused(ShellNudges.PIPED_TEST_RUN, filter="tail")
    story.expect_stack(Ready)


@story(WorkingAgent, mode=BUILDER_MODE, scope=AgentRole.MAIN)
def test_a_test_run_through_an_alias_with_a_reader_piped_into_a_filter_is_refused(story):
    story.agent_runs('alias add checks "pytest -q" --reader pytest')
    story.expect_command_passed()
    story.agent_runs_in_the_shell("journal checks | tail -5")
    story.expect_refused(ShellNudges.PIPED_TEST_RUN, filter="tail")
    story.expect_stack(Ready)


@story(WorkingAgent, mode=BUILDER_MODE, scope=AgentRole.MAIN)
def test_a_test_run_alone_goes_through(story):
    story.agent_runs_in_the_shell("pytest -q")
    story.expect_allowed()
    story.expect_stack(Ready)


@story(WorkingAgent, mode=BUILDER_MODE, scope=AgentRole.MAIN)
def test_a_shell_loop_polling_the_journal_is_refused(story):
    story.agent_runs_in_the_shell("while true; do journal output status 4; sleep 5; done")
    story.expect_refused(ShellNudges.JOURNAL_POLL, n="4")
    story.expect_stack(Ready)


@story(WorkingAgent, mode=BUILDER_MODE, scope=AgentRole.MAIN)
def test_a_shell_loop_with_no_journal_command_goes_through(story):
    story.agent_runs_in_the_shell("for f in a b; do echo $f; done")
    story.expect_allowed()
    story.expect_stack(Ready)


@story(WorkingAgent, mode=BUILDER_MODE, scope=AgentRole.MAIN)
def test_a_cd_out_of_the_project_is_refused(story):
    story.agent_runs_in_the_shell("cd /tmp")
    story.expect_refused(ShellNudges.FOLDER_CHANGE_REFUSAL, target="/tmp")
    story.expect_stack(Ready)


@story(WorkingAgent, mode=BUILDER_MODE, scope=AgentRole.MAIN)
def test_a_cd_in_a_subshell_goes_through(story):
    story.agent_runs_in_the_shell("( cd /tmp && ls )")
    story.expect_allowed()
    story.expect_stack(Ready)


@story(WorkingAgent, mode=BUILDER_MODE, scope=AgentRole.MAIN)
def test_the_projects_absolute_path_is_refused_and_the_relative_line_named(story):
    story.agent_runs_in_the_shell(f"ls {story.project_root()}/src")
    story.expect_refused(ShellNudges.PROJECT_PATH_REFUSAL, line="ls src")
    story.expect_stack(Ready)


@story(WorkingAgent, mode=BUILDER_MODE, scope=AgentRole.MAIN)
def test_a_relative_path_goes_through(story):
    story.agent_runs_in_the_shell("ls src")
    story.expect_allowed()
    story.expect_stack(Ready)


@story(StartedTask, mode=BUILDER_MODE, scope=AgentRole.MAIN)
def test_a_journal_command_chained_with_another_is_refused_with_a_task_in_hand(story):
    story.agent_runs_in_the_shell("journal task list && ls")
    story.expect_refused(ShellNudges.JOURNAL_COMMAND_ISOLATION)
    story.expect_task(story.start.started_task, state=TaskState.STARTED)
    story.expect_stack(Ready, Working)
