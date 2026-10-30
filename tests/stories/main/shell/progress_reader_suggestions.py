from journal.features.shell.listeners.untotaled_run_record import TOTAL_WAIT_SECONDS
from journal.features.shell.shell_nudges import ShellNudges
from journal.features.tasks.states.ready import Ready
from journal.features.workers.workers_options import BUILDER_MODE
from journal.support.agent_role import AgentRole
from tests.stories.builder.story_marks import story
from tests.stories.fixtures.main.working_agent import WorkingAgent

TEST_RUN = "./dots/gotestsum -q"
DOTS = "........"
COUNTED = ("file 3/10 done", "file 4/10 done", "file 5/10 done")
STARTING = ("file 0/10 done",)
DOTS_READER = "reader add dots --pattern '\\.' --about 'the test dots'"
FILES_READER = "reader add files --pattern 'done' --about 'the files done'"


@story(WorkingAgent, mode=BUILDER_MODE, subject=AgentRole.MAIN)
def test_a_run_printing_a_count_of_a_total_its_reader_shows_no_bar_for_is_told_the_pattern_that_reads_it(story):
    run = story.agent_has_a_background_run_printing(story.agents.subject, TEST_RUN, *COUNTED)
    story.agent_runs(story.agents.subject, FILES_READER)
    story.agent_runs(story.agents.subject, f"output watch {run} --reader files")
    result = story.agent_is_quiet_past(story.agents.subject, TOTAL_WAIT_SECONDS)
    result.expect_agent_told(story.agents.subject, ShellNudges.RUN_COUNT_UNSHOWN, n=run)
    result.expect_agent_not_told(story.agents.subject, ShellNudges.RUN_TOTAL_MISSING)
    story.expect_stack(story.agents.subject, Ready)


@story(WorkingAgent, mode=BUILDER_MODE, subject=AgentRole.MAIN)
def test_a_run_whose_reader_shows_its_progress_is_never_told_even_while_its_bar_stands_at_nothing(story):
    story.agent_runs(story.agents.subject, f"{FILES_READER} --progress '(\\d+)/(\\d+)'")
    run = story.agent_has_a_background_run_printing(story.agents.subject, TEST_RUN, *STARTING)
    story.agent_runs(story.agents.subject, f"output watch {run} --reader files")
    result = story.agent_is_quiet_past(story.agents.subject, TOTAL_WAIT_SECONDS)
    result.expect_agent_not_told(story.agents.subject, ShellNudges.RUN_TOTAL_MISSING)
    result.expect_agent_not_told(story.agents.subject, ShellNudges.RUN_COUNT_UNSHOWN)
    story.expect_stack(story.agents.subject, Ready)


@story(WorkingAgent, mode=BUILDER_MODE, subject=AgentRole.MAIN)
def test_a_run_that_is_not_a_test_run_or_a_build_is_never_told(story):
    story.agent_runs(story.agents.subject, DOTS_READER)
    run = story.agent_has_a_background_run_printing(story.agents.subject, "./dots/tail.sh", DOTS)
    story.agent_runs(story.agents.subject, f"output watch {run} --reader dots")
    result = story.agent_is_quiet_past(story.agents.subject, TOTAL_WAIT_SECONDS)
    result.expect_agent_not_told(story.agents.subject, ShellNudges.RUN_TOTAL_MISSING)
    story.expect_stack(story.agents.subject, Ready)


@story(WorkingAgent, mode=BUILDER_MODE, subject=AgentRole.MAIN)
def test_a_test_run_whose_reader_shows_no_progress_is_told_once_per_version_of_the_reader(story):
    story.agent_runs(story.agents.subject, DOTS_READER)
    first = story.agent_has_a_background_run_printing(story.agents.subject, TEST_RUN, DOTS)
    story.agent_runs(story.agents.subject, f"output watch {first} --reader dots")
    result = story.agent_is_quiet_past(story.agents.subject, TOTAL_WAIT_SECONDS)
    result.expect_agent_told(story.agents.subject, ShellNudges.RUN_TOTAL_MISSING, n=first)
    result = story.agent_is_quiet_past(story.agents.subject, TOTAL_WAIT_SECONDS)
    result.expect_agent_not_told(story.agents.subject, ShellNudges.RUN_TOTAL_MISSING)
    story.recorded_run_ends(first)
    second = story.agent_has_a_background_run_printing(story.agents.subject, TEST_RUN, DOTS)
    story.agent_runs(story.agents.subject, f"output watch {second} --reader dots")
    result = story.agent_is_quiet_past(story.agents.subject, TOTAL_WAIT_SECONDS)
    result.expect_agent_not_told(story.agents.subject, ShellNudges.RUN_TOTAL_MISSING)
    story.recorded_run_ends(second)
    story.agent_runs(story.agents.subject, "reader add dots --pattern '\\.+' --about 'the test dots'")
    third = story.agent_has_a_background_run_printing(story.agents.subject, TEST_RUN, DOTS)
    story.agent_runs(story.agents.subject, f"output watch {third} --reader dots")
    result = story.agent_is_quiet_past(story.agents.subject, TOTAL_WAIT_SECONDS)
    result.expect_agent_told(story.agents.subject, ShellNudges.RUN_TOTAL_MISSING, n=third)
    story.expect_stack(story.agents.subject, Ready)
