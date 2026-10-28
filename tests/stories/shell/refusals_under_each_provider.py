from journal.features.shell.shell_nudges import ShellNudges
from journal.providers.claude import Claude
from journal.providers.codex import Codex
from tests.stories.builder.story_marks import provider, story
from tests.stories.fixtures.agent_at_work import AgentAtWork


@story(AgentAtWork)
@provider(Claude)
def test_a_refused_command_line_is_refused_in_claudes_answer(story):
    story.agent_runs_in_the_shell("journal task list && ls")
    story.expect_refused(ShellNudges.JOURNAL_COMMAND_ISOLATION)


@story(AgentAtWork)
@provider(Codex)
def test_a_refused_command_line_is_refused_in_codexs_answer(story):
    story.agent_runs_in_the_shell("journal task list && ls")
    story.expect_refused(ShellNudges.JOURNAL_COMMAND_ISOLATION)
