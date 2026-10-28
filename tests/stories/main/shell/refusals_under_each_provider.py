from journal.features.shell.shell_nudges import ShellNudges
from journal.features.tasks.states.ready import Ready
from journal.providers.codex import Codex
from journal.features.workers.workers_options import BUILDER_MODE
from tests.stories.builder.story_marks import provider, story
from tests.stories.fixtures.main.working_agent import WorkingAgent


@story(WorkingAgent, mode=BUILDER_MODE)
@provider(Codex)
def test_a_refused_command_line_is_refused_in_codexs_answer(story):
    story.agent_runs_in_the_shell("journal plan list && ls")
    story.expect_refused(ShellNudges.JOURNAL_COMMAND_ISOLATION)
    story.expect_stack(Ready)
