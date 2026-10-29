from journal.features.tasks.states.ready import Ready
from journal.providers.codex import Codex
from journal.features.workers.workers_options import BUILDER_MODE
from journal.support.agent_role import AgentRole
from tests.stories.builder.story_marks import provider, story
from tests.stories.fixtures.main.working_agent import WorkingAgent

LONG_LINE = "make build"


@story(WorkingAgent, mode=BUILDER_MODE, scope=AgentRole.MAIN)
@provider(Codex)
def test_a_codex_shell_line_is_handed_to_the_journals_runner(story):
    story.agent_runs_in_the_shell(LONG_LINE)
    story.expect_allowed()
    story.expect_tool_input_changed(command=Codex.runner_command(LONG_LINE))
    story.expect_stack(Ready)


@story(WorkingAgent, mode=BUILDER_MODE, scope=AgentRole.MAIN)
@provider(Codex)
def test_a_codex_shell_line_handed_to_bash_reaches_the_runner_with_its_shell(story):
    story.agent_runs_in_the_shell_as_argv("bash", "-lc", LONG_LINE)
    story.expect_allowed()
    story.expect_tool_input_changed(command=Codex.runner_command(Codex.shell_line(["bash", "-lc", LONG_LINE]).line_with_shell()))
    story.expect_stack(Ready)
