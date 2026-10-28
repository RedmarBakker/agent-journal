from journal.features.shell.shell_nudges import ShellNudges
from journal.providers.codex import Codex
from tests.stories.builder.story_marks import provider, story
from tests.stories.fixtures.working_agent import WorkingAgent


@story(WorkingAgent)
@provider(Codex)
def test_a_refused_command_line_is_refused_in_codexs_answer(story):
    story.agent_runs_in_the_shell("journal task list && ls")
    story.expect_refused(ShellNudges.JOURNAL_COMMAND_ISOLATION)
