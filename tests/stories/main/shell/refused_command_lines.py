from journal.features.messages.messages_nudges import MessagesNudges
from journal.features.shell.shell_nudges import ShellNudges
from journal.features.tasks.states.ready import Ready
from journal.features.tasks.states.working import Working
from journal.models.task_state import TaskState
from journal.support.agent_role import AgentRole
from tests.stories.builder.story_marks import story
from tests.stories.fixtures.main.started_task import StartedTask
from tests.stories.fixtures.main.working_agent import WorkingAgent


@story(WorkingAgent, subject=AgentRole.MAIN)
def test_a_journal_command_chained_before_another_is_refused(story):
    result = story.agent_runs_in_the_shell(story.agents.subject, "journal task list && ls")
    result.expect_refused(story.agents.subject, ShellNudges.JOURNAL_COMMAND_ISOLATION)
    story.expect_stack(story.agents.subject, Ready)


@story(WorkingAgent, subject=AgentRole.MAIN)
def test_a_journal_command_chained_after_another_is_refused(story):
    result = story.agent_runs_in_the_shell(story.agents.subject, "ls; journal task list")
    result.expect_refused(story.agents.subject, ShellNudges.JOURNAL_COMMAND_ISOLATION)
    story.expect_stack(story.agents.subject, Ready)


@story(WorkingAgent, subject=AgentRole.MAIN)
def test_a_message_read_piped_into_a_filter_is_refused(story):
    result = story.agent_runs_in_the_shell(story.agents.subject, "journal message read 4 | head -3")
    result.expect_refused(story.agents.subject, MessagesNudges.FULL_MESSAGE_READ)
    story.expect_stack(story.agents.subject, Ready)


@story(WorkingAgent, subject=AgentRole.MAIN)
def test_a_journal_command_read_whole_piped_into_a_filter_is_refused(story):
    result = story.agent_runs_in_the_shell(story.agents.subject, "journal task show 4 | head -3")
    result.expect_refused(story.agents.subject, ShellNudges.PIPED_JOURNAL_COMMAND, command="task show", filter="head")
    story.expect_stack(story.agents.subject, Ready)


@story(WorkingAgent, subject=AgentRole.MAIN)
def test_a_test_run_piped_into_a_filter_is_refused(story):
    result = story.agent_runs_in_the_shell(story.agents.subject, "pytest -q | tail -5")
    result.expect_refused(story.agents.subject, ShellNudges.PIPED_TEST_RUN, filter="tail")
    story.expect_stack(story.agents.subject, Ready)


@story(WorkingAgent, subject=AgentRole.MAIN)
def test_a_test_run_through_an_alias_with_a_reader_piped_into_a_filter_is_refused(story):
    result = story.agent_runs(story.agents.subject, 'alias add checks "pytest -q" --reader pytest')
    result.expect_command_passed()
    result = story.agent_runs_in_the_shell(story.agents.subject, "journal checks | tail -5")
    result.expect_refused(story.agents.subject, ShellNudges.PIPED_TEST_RUN, filter="tail")
    story.expect_stack(story.agents.subject, Ready)


@story(WorkingAgent, subject=AgentRole.MAIN)
def test_a_test_run_alone_goes_through(story):
    result = story.agent_runs_in_the_shell(story.agents.subject, "pytest -q")
    result.expect_allowed()
    story.expect_stack(story.agents.subject, Ready)


@story(WorkingAgent, subject=AgentRole.MAIN)
def test_a_shell_loop_polling_the_journal_is_refused(story):
    result = story.agent_runs_in_the_shell(story.agents.subject, "while true; do journal output status 4; sleep 5; done")
    result.expect_refused(story.agents.subject, ShellNudges.JOURNAL_POLL, n="4")
    story.expect_stack(story.agents.subject, Ready)


@story(WorkingAgent, subject=AgentRole.MAIN)
def test_a_shell_loop_with_no_journal_command_goes_through(story):
    result = story.agent_runs_in_the_shell(story.agents.subject, "for f in a b; do echo $f; done")
    result.expect_allowed()
    story.expect_stack(story.agents.subject, Ready)


@story(WorkingAgent, subject=AgentRole.MAIN)
def test_a_cd_out_of_the_project_is_refused(story):
    result = story.agent_runs_in_the_shell(story.agents.subject, "cd /tmp")
    result.expect_refused(story.agents.subject, ShellNudges.FOLDER_CHANGE_REFUSAL, target="/tmp")
    story.expect_stack(story.agents.subject, Ready)


@story(WorkingAgent, subject=AgentRole.MAIN)
def test_a_cd_in_a_subshell_goes_through(story):
    result = story.agent_runs_in_the_shell(story.agents.subject, "( cd /tmp && ls )")
    result.expect_allowed()
    story.expect_stack(story.agents.subject, Ready)


@story(WorkingAgent, subject=AgentRole.MAIN)
def test_the_projects_absolute_path_is_refused_and_the_relative_line_named(story):
    result = story.agent_runs_in_the_shell(story.agents.subject, f"ls {story.project_root()}/src")
    result.expect_refused(story.agents.subject, ShellNudges.PROJECT_PATH_REFUSAL, line="ls src")
    story.expect_stack(story.agents.subject, Ready)


@story(WorkingAgent, subject=AgentRole.MAIN)
def test_a_relative_path_goes_through(story):
    result = story.agent_runs_in_the_shell(story.agents.subject, "ls src")
    result.expect_allowed()
    story.expect_stack(story.agents.subject, Ready)


@story(StartedTask, subject=AgentRole.MAIN)
def test_a_journal_command_chained_with_another_is_refused_with_a_task_in_hand(story):
    result = story.agent_runs_in_the_shell(story.agents.subject, "journal task list && ls")
    result.expect_refused(story.agents.subject, ShellNudges.JOURNAL_COMMAND_ISOLATION)
    story.expect_task(story.tasks.started, state=TaskState.STARTED)
    story.expect_stack(story.agents.subject, Ready, Working)
