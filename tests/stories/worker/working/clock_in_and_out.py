from journal.engine.engine_nudges import EngineNudges
from journal.engine.states.void import Void
from journal.features.workers.states.working_task import WorkingTask
from journal.features.workers.workers_nudges import WorkersNudges
from journal.models.worker_state import WorkerState
from journal.features.workers.workers_options import BUILDER_MODE
from tests.stories.builder.story_marks import story
from tests.stories.fixtures.worker.dispatched_worker import DispatchedWorker
from tests.stories.fixtures.worker.working_worker import WorkingWorker


@story(DispatchedWorker, mode=BUILDER_MODE)
def test_a_worker_that_writes_before_it_clocks_in_is_refused(story):
    story.worker_writes(story.start.worker, "parser.py")
    story.expect_refused(EngineNudges.JOBLESS_HELPER)
    story.expect_worker(story.start.worker, state=WorkerState.DISPATCHED)
    story.expect_stack(Void)


@story(WorkingWorker, mode=BUILDER_MODE)
def test_a_worker_stop_with_open_todos_is_told_them(story):
    story.worker_runs(story.start.worker, "todo add 'read the grammar'")
    story.worker_stops(story.start.worker)
    story.expect_agent_told(WorkersNudges.OPEN_TODOS, count=1)
    story.expect_task(story.start.briefed, delegated=True)
    story.expect_stack(Void, WorkingTask)


@story(WorkingWorker, mode=BUILDER_MODE)
def test_a_worker_stop_with_every_todo_checked_is_told_nothing_of_them(story):
    story.worker_runs(story.start.worker, "todo add 'read the grammar'")
    story.worker_runs(story.start.worker, "todo check 1")
    story.worker_stops(story.start.worker)
    story.expect_agent_not_told(WorkersNudges.OPEN_TODOS)
    story.expect_task(story.start.briefed, delegated=True)
    story.expect_stack(Void, WorkingTask)


@story(WorkingWorker, mode=BUILDER_MODE)
def test_a_worker_never_runs_git(story):
    story.worker_runs_in_the_shell(story.start.worker, "git commit -am done")
    story.expect_refused(WorkersNudges.WORKER_GIT_REFUSAL)
    story.expect_task(story.start.briefed, delegated=True)
    story.expect_stack(Void, WorkingTask)
