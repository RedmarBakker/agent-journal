from journal.features.shell.shell_nudges import ShellNudges
from journal.features.tasks.states.external_wait import ExternalWait
from journal.features.tasks.states.ready import Ready
from journal.features.workers.workers_options import BUILDER_MODE
from journal.support.agent_role import AgentRole
from tests.stories.builder.story_marks import story
from tests.stories.fixtures.main.working_agent import WorkingAgent

PROCESS_LOOP = "until ! pgrep -f update_matrix_run.py; do sleep 5; done"


@story(WorkingAgent, mode=BUILDER_MODE, subject=AgentRole.MAIN)
def test_a_loop_that_only_sleeps_until_a_process_ends_is_run_as_a_wait_named_for_the_process(story):
    story.agent_runs_a_command(story.agents.subject, PROCESS_LOOP)
    story.last_step.expect_shell_text("waiting on check")
    story.last_step.expect_agent_told(story.agents.subject, ShellNudges.SLEEP_LOOP_WAIT, title="update_matrix_run.py ends", script="! pgrep -f update_matrix_run.py")
    story.expect_stack(story.agents.subject, Ready, ExternalWait)


@story(WorkingAgent, mode=BUILDER_MODE, subject=AgentRole.MAIN)
def test_a_loop_that_works_besides_sleeping_runs_untouched_and_one_that_sleeps_while_a_check_passes_waits_until_it_fails(story):
    story.agent_runs_a_command(story.agents.subject, "until test -e done.flag; do touch done.flag; sleep 1; done")
    story.last_step.expect_shell_exit(0)
    story.last_step.expect_agent_not_told(story.agents.subject, ShellNudges.SLEEP_LOOP_WAIT)
    story.agent_runs_a_command(story.agents.subject, "while test -e build.lock; do sleep 2; done")
    story.last_step.expect_agent_told(story.agents.subject, ShellNudges.SLEEP_LOOP_WAIT, title="`! test -e build.lock` passes", script="! test -e build.lock")
    story.expect_stack(story.agents.subject, Ready, ExternalWait)


@story(WorkingAgent, mode=BUILDER_MODE, subject=AgentRole.MAIN)
def test_a_line_that_only_sleeps_is_refused(story):
    result = story.agent_runs_in_the_shell(story.agents.subject, "sleep 30")
    result.expect_refused(story.agents.subject, ShellNudges.SLEEP_LINE_REFUSAL)
    story.expect_stack(story.agents.subject, Ready)
