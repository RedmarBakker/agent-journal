from journal.engine.states.void import Void
from journal.features.workers.states.working_task import WorkingTask
from journal.features.workers.workers_nudges import WorkersNudges
from journal.features.workers.workers_options import BUILDER_MODE, JOURNAL_TESTING, MERGER_TESTING, TEST_BUDGET, WORKER_TESTING, WorkersOptions
from tests.stories.builder.story_marks import setting, story
from tests.stories.fixtures.worker.working_worker import WorkingWorker

TEST_LINE = "python3 -m pytest tests/test_parser.py"


@story(WorkingWorker, mode=BUILDER_MODE)
@setting(WorkersOptions.TESTING, MERGER_TESTING)
def test_a_worker_may_not_run_tests_when_the_merger_runs_them(story):
    story.worker_runs_in_the_shell(story.start.worker, TEST_LINE)
    story.expect_refused(WorkersNudges.TEST_HANDOVER)
    story.expect_stack(Void, WorkingTask)


@story(WorkingWorker, mode=BUILDER_MODE)
@setting(WorkersOptions.TESTING, TEST_BUDGET)
def test_a_worker_under_a_test_budget_runs_tests_only_through_a_turn(story):
    story.worker_runs_in_the_shell(story.start.worker, TEST_LINE)
    story.expect_refused(WorkersNudges.TEST_BUDGET_REFUSAL)
    story.expect_stack(Void, WorkingTask)


@story(WorkingWorker, mode=BUILDER_MODE)
@setting(WorkersOptions.TESTING, JOURNAL_TESTING)
def test_a_worker_whose_tests_the_journal_runs_names_them_instead_of_running_them(story):
    story.worker_runs_in_the_shell(story.start.worker, TEST_LINE)
    story.expect_refused(WorkersNudges.JOURNAL_TESTS_REFUSAL)
    story.expect_stack(Void, WorkingTask)


@story(WorkingWorker, mode=BUILDER_MODE)
@setting(WorkersOptions.TESTING, WORKER_TESTING)
def test_a_worker_that_runs_the_tests_it_wrote_may_run_them(story):
    story.worker_runs_in_the_shell(story.start.worker, TEST_LINE)
    story.expect_allowed()
    story.expect_task(story.start.briefed, delegated=True)
    story.expect_stack(Void, WorkingTask)
