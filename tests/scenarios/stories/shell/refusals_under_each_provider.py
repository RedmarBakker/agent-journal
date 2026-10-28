from journal.features.shell.shell_nudges import ShellNudges
from journal.providers.claude import Claude
from journal.providers.codex import Codex
from tests.scenarios.builder.story_values import provider, scenario
from tests.scenarios.state_fixtures.agent_at_work import AgentAtWork


@scenario(AgentAtWork)
@provider(Claude)
def test_a_refused_command_line_is_refused_in_claudes_answer(scenario):
    scenario.agent_runs_in_the_shell("journal task list && ls")
    scenario.expect_refused(ShellNudges.JOURNAL_COMMAND_ISOLATION)


@scenario(AgentAtWork)
@provider(Codex)
def test_a_refused_command_line_is_refused_in_codexs_answer(scenario):
    scenario.agent_runs_in_the_shell("journal task list && ls")
    scenario.expect_refused(ShellNudges.JOURNAL_COMMAND_ISOLATION)
