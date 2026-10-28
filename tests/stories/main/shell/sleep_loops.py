from journal.features.shell.shell_nudges import ShellNudges
from journal.features.tasks.states.external_wait import ExternalWait
from journal.features.tasks.states.ready import Ready
from journal.features.workers.workers_options import BUILDER_MODE
from journal.support.agent_role import AgentRole
from tests.stories.builder.story_marks import story
from tests.stories.fixtures.main.working_agent import WorkingAgent

PROCESS_LOOP = "until ! pgrep -f update_matrix_run.py; do sleep 5; done"


@story(WorkingAgent, mode=BUILDER_MODE, scope=AgentRole.MAIN)
def test_a_loop_that_only_sleeps_until_a_process_ends_is_run_as_a_wait_named_for_the_process(story):
    story.agent_runs_a_command(PROCESS_LOOP)
    story.expect_shell_text("waiting on check")
    story.expect_agent_told(ShellNudges.SLEEP_LOOP_WAIT, title="update_matrix_run.py ends", script="! pgrep -f update_matrix_run.py")
    story.expect_stack(Ready, ExternalWait)


@story(WorkingAgent, mode=BUILDER_MODE, scope=AgentRole.MAIN)
def test_a_loop_that_works_besides_sleeping_runs_untouched_and_one_that_sleeps_while_a_check_passes_waits_until_it_fails(story):
    story.agent_runs_a_command("until test -e done.flag; do touch done.flag; sleep 1; done")
    story.expect_shell_exit(0)
    story.expect_agent_not_told(ShellNudges.SLEEP_LOOP_WAIT)
    story.agent_runs_a_command("while test -e build.lock; do sleep 2; done")
    story.expect_agent_told(ShellNudges.SLEEP_LOOP_WAIT, title="`! test -e build.lock` passes", script="! test -e build.lock")
    story.expect_stack(Ready, ExternalWait)


@story(WorkingAgent, mode=BUILDER_MODE, scope=AgentRole.MAIN)
def test_a_line_that_only_sleeps_is_refused(story):
    story.agent_runs_in_the_shell("sleep 30")
    story.expect_refused(ShellNudges.SLEEP_LINE_REFUSAL)
    story.expect_stack(Ready)
