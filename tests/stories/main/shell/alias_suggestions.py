from journal.features.shell.shell_conduct import ALIAS_RUNS
from journal.features.shell.shell_nudges import ShellNudges
from journal.features.tasks.states.ready import Ready
from journal.features.workers.workers_options import BUILDER_MODE
from tests.stories.builder.story_marks import story
from tests.stories.fixtures.main.working_agent import WorkingAgent


@story(WorkingAgent, mode=BUILDER_MODE)
def test_a_line_run_the_set_times_is_offered_as_an_alias_once_on_the_last_and_not_before(story):
    for _ in range(ALIAS_RUNS - 1):
        story.agent_runs_in_the_shell("make build site")
    story.expect_agent_not_told(ShellNudges.ALIAS_SUGGESTION)
    story.agent_runs_in_the_shell("make build site")
    story.expect_allowed()
    story.expect_agent_told(ShellNudges.ALIAS_SUGGESTION)
    story.agent_runs_in_the_shell("make build site")
    story.expect_agent_not_told(ShellNudges.ALIAS_SUGGESTION)
    story.expect_stack(Ready)


@story(WorkingAgent, mode=BUILDER_MODE)
def test_a_journal_command_run_again_and_again_is_never_offered_as_an_alias(story):
    for _ in range(ALIAS_RUNS):
        story.agent_runs_in_the_shell("journal task list")
    story.expect_agent_not_told(ShellNudges.ALIAS_SUGGESTION)
    story.expect_stack(Ready)


@story(WorkingAgent, mode=BUILDER_MODE)
def test_a_read_run_again_and_again_is_never_offered_as_an_alias(story):
    for _ in range(ALIAS_RUNS):
        story.agent_runs_in_the_shell("cat src/app.py")
    story.expect_agent_not_told(ShellNudges.ALIAS_SUGGESTION)
    story.expect_stack(Ready)


@story(WorkingAgent, mode=BUILDER_MODE)
def test_a_line_of_one_word_is_never_offered_as_an_alias(story):
    for _ in range(ALIAS_RUNS):
        story.agent_runs_in_the_shell("pwd")
    story.expect_agent_not_told(ShellNudges.ALIAS_SUGGESTION)
    story.expect_stack(Ready)
