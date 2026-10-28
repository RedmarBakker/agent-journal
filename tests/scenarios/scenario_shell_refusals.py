from journal.features.messages.messages_nudges import MessagesNudges
from journal.features.shell.shell_nudges import ShellNudges
from tests.scenarios.builder.story_values import scenario, values
from tests.scenarios.state_fixtures.agent_at_work import AgentAtWork


@scenario(AgentAtWork)
@values(["journal task list && ls", "ls; journal task list"])
def test_a_journal_command_runs_alone(scenario, value):
    scenario.agent_runs_in_the_shell(value)
    scenario.expect_refused(ShellNudges.JOURNAL_COMMAND_ISOLATION)


@scenario(AgentAtWork)
def test_a_message_read_piped_into_a_filter_is_refused(scenario):
    scenario.agent_runs_in_the_shell("journal message unread | head -3")
    scenario.expect_refused(MessagesNudges.FULL_MESSAGE_READ)


@scenario(AgentAtWork)
def test_a_test_run_piped_into_a_filter_is_refused(scenario):
    scenario.agent_runs_in_the_shell("pytest -q | tail -5")
    scenario.expect_refused(ShellNudges.PIPED_TEST_RUN)


@scenario(AgentAtWork)
def test_a_shell_loop_polling_the_journal_is_refused(scenario):
    scenario.agent_runs_in_the_shell("while true; do journal output status 4; sleep 5; done")
    scenario.expect_refused(ShellNudges.JOURNAL_POLL)
