from journal.engine.engine_nudges import EngineNudges
from journal.engine.states.void import Void
from journal.features.tasks.states.external_wait import ExternalWait
from journal.features.tasks.states.ready import Ready
from journal.features.workers.states.working_task import WorkingTask
from journal.features.workers.workers_nudges import WorkersNudges
from journal.models.worker_state import WorkerState
from tests.stories.builder.story_marks import story
from tests.stories.fixtures.briefed_task import BriefedTask
from tests.stories.fixtures.clocked_in_worker import ClockedInWorker
from tests.stories.fixtures.worker_delivered import WorkerDelivered


@story(ClockedInWorker, end=[Ready, ExternalWait])
def test_a_worker_clocked_in_works_in_its_working_state(story):
    story.expect_worker_stack(story.start.worker, Void, WorkingTask)
    story.expect_worker(story.start.worker, state=WorkerState.READY)
    story.expect_task(story.start.briefed, delegated=True)


@story(WorkerDelivered, end=[Ready])
def test_a_worker_leaves_its_working_state_at_clock_out(story):
    story.expect_worker_stack(story.start.worker, Void)
    story.expect_worker(story.start.worker, state=WorkerState.DELIVERED)
    story.expect_task(story.start.briefed, delegated=True)


@story(ClockedInWorker, end=[Ready, ExternalWait])
def test_a_worker_clocks_in_only_once_each_time_it_is_sent(story):
    story.worker_tries(story.start.worker, "clock-in")
    story.expect_command_refused()
    story.expect_worker_stack(story.start.worker, Void, WorkingTask)


@story(BriefedTask, end=[Ready])
def test_a_worker_whose_task_was_cancelled_before_it_clocked_in_cannot_clock_in(story):
    worker = story.agent_dispatches_worker("Lady Lovelace", story.start.briefed)
    story.user_cancels_task(story.start.briefed, "not needed")
    story.worker_tries(worker, "clock-in")
    story.expect_command_refused()
    story.expect_worker_stack(worker, Void)


@story(BriefedTask, end=[Ready])
def test_only_a_worker_clocks_in(story):
    story.agent_runs("clock-in")
    story.expect_command_refused()
    story.expect_task(story.start.briefed, delegated=False)


@story(BriefedTask, end=[Ready, ExternalWait])
def test_a_worker_that_writes_before_it_clocks_in_is_refused(story):
    worker = story.agent_dispatches_worker("Lady Lovelace", story.start.briefed)
    story.worker_writes(worker, "parser.py")
    story.expect_refused(EngineNudges.JOBLESS_HELPER)
    story.expect_worker(worker, state=WorkerState.DISPATCHED)


@story(ClockedInWorker, end=[Ready, ExternalWait])
def test_a_clock_out_with_a_point_unproved_is_refused(story):
    story.worker_proves(story.start.worker, 1, "parser.py:12, test_reads passes")
    story.worker_tries(story.start.worker, "clock-out 'the parser is done'")
    story.expect_command_refused()
    story.expect_agent_not_told(WorkersNudges.WORK_READY)
    story.expect_worker(story.start.worker, state=WorkerState.READY)


@story(ClockedInWorker, end=[Ready, ExternalWait])
def test_a_proof_for_a_point_the_brief_does_not_have_is_refused(story):
    story.worker_tries(story.start.worker, "proof 3 'parser.py:40'")
    story.expect_command_refused()
    story.expect_worker_stack(story.start.worker, Void, WorkingTask)


@story(ClockedInWorker, end=[Ready, ExternalWait])
def test_a_worker_stop_with_open_todos_is_told_them(story):
    story.worker_runs(story.start.worker, "todo add 'read the grammar'")
    story.worker_stops(story.start.worker)
    story.expect_agent_told(WorkersNudges.OPEN_TODOS, count=1)
    story.expect_worker_stack(story.start.worker, Void, WorkingTask)


@story(ClockedInWorker, end=[Ready, ExternalWait])
def test_a_worker_stop_with_every_todo_checked_is_told_nothing_of_them(story):
    story.worker_runs(story.start.worker, "todo add 'read the grammar'")
    story.worker_runs(story.start.worker, "todo check 1")
    story.worker_stops(story.start.worker)
    story.expect_agent_not_told(WorkersNudges.OPEN_TODOS)


@story(ClockedInWorker, end=[Ready, ExternalWait])
def test_a_worker_never_runs_git(story):
    story.worker_runs_in_the_shell(story.start.worker, "git commit -am done")
    story.expect_refused(WorkersNudges.WORKER_GIT_REFUSAL)
    story.expect_worker_stack(story.start.worker, Void, WorkingTask)
