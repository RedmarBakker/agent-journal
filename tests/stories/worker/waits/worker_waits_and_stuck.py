from journal.engine.states.void import Void
from journal.features.tasks.states.external_wait import ExternalWait
from journal.features.tasks.states.impasse import Impasse
from journal.features.workers.states.working_task import WorkingTask
from journal.features.workers.workers_options import BUILDER_MODE
from tests.stories.builder.story_marks import story
from tests.stories.fixtures.worker.working_worker import WorkingWorker


@story(WorkingWorker, mode=BUILDER_MODE)
def test_a_worker_that_awaits_waits_over_its_work_until_its_own_tool_use(story):
    story.agent_runs("await 'the build of the parser' --until false")
    story.expect_command_passed()
    story.expect_stack(Void, WorkingTask, ExternalWait)
    story.agent_reads()
    story.expect_task(story.start.briefed, delegated=True)
    story.expect_stack(Void, WorkingTask)


@story(WorkingWorker, mode=BUILDER_MODE)
def test_a_journal_command_leaves_the_workers_wait(story):
    story.agent_runs("await 'the build of the parser' --until false")
    story.agent_runs("todo add 'read the grammar'")
    story.expect_task(story.start.briefed, delegated=True)
    story.expect_stack(Void, WorkingTask, ExternalWait)


@story(WorkingWorker, mode=BUILDER_MODE)
def test_a_worker_clearing_its_wait_is_back_at_its_work(story):
    story.agent_runs("await 'the build of the parser' --until false")
    story.agent_runs("await clear")
    story.expect_command_passed()
    story.expect_task(story.start.briefed, delegated=True)
    story.expect_stack(Void, WorkingTask)


@story(WorkingWorker, mode=BUILDER_MODE)
def test_a_worker_that_says_it_is_stuck_waits_until_its_next_tool_use(story):
    story.agent_runs("stuck 'the grammar file is missing'")
    story.expect_stack(Void, WorkingTask, Impasse)
    story.agent_reads()
    story.expect_task(story.start.briefed, delegated=True)
    story.expect_stack(Void, WorkingTask)
