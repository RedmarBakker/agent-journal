from journal.engine.states.void import Void
from journal.features.tasks.states.ready import Ready
from journal.features.workers.workers_nudges import WorkersNudges
from journal.models.task_state import TaskState
from journal.models.worker_state import WorkerState
from tests.stories.builder.story_marks import story
from tests.stories.fixtures.clocked_in_worker import ClockedInWorker
from tests.stories.fixtures.plan_worker import PlanWorker
from tests.stories.fixtures.worker_delivered import WorkerDelivered


@story(ClockedInWorker, end=[Ready])
def test_the_user_completing_a_workers_task_releases_the_worker_and_tells_it_to_stop(story):
    story.user_completes_task(story.start.briefed, "done by hand")
    story.expect_worker(story.start.worker, state=WorkerState.RELEASED)
    story.expect_agent_told(WorkersNudges.USER_CLOSURE, task=story.start.briefed)
    story.expect_worker_stack(story.start.worker, Void)


@story(ClockedInWorker, end=[Ready])
def test_the_user_cancelling_a_workers_task_leaves_it_cancelled_and_undelegated(story):
    story.user_cancels_task(story.start.briefed, "not needed")
    story.expect_task(story.start.briefed, state=TaskState.CANCELLED, delegated=False)
    story.expect_worker(story.start.worker, state=WorkerState.RELEASED)


@story(ClockedInWorker, end=[Ready])
def test_the_user_pausing_a_workers_task_takes_it_from_the_worker(story):
    story.user_pauses_task(story.start.briefed, "later")
    story.expect_task(story.start.briefed, state=TaskState.PAUSED)
    story.expect_worker(story.start.worker, state=WorkerState.RELEASED)


@story(PlanWorker, end=[Ready])
def test_releasing_a_worker_opens_its_queued_tasks_again(story):
    story.agent_runs(f"worker release {story.start.worker}")
    story.expect_command_passed()
    story.expect_task(story.start.second_task, state=TaskState.OPEN, delegated=False)
    story.expect_worker(story.start.worker, state=WorkerState.RELEASED)


@story(WorkerDelivered, end=[Ready])
def test_a_task_the_user_cancels_while_its_work_waits_releases_the_worker_unmerged(story):
    story.user_cancels_task(story.start.briefed, "not needed")
    story.expect_worker(story.start.worker, state=WorkerState.RELEASED)
    story.expect_task(story.start.briefed, state=TaskState.CANCELLED)


@story(ClockedInWorker, end=[Ready])
def test_stopping_a_worker_tells_the_agent_it_ended_without_a_report(story):
    story.agent_runs(f"worker stop {story.start.worker}")
    story.expect_command_passed()
    story.expect_worker(story.start.worker, state=WorkerState.STOPPED)
    story.expect_agent_told(WorkersNudges.WORKER_STOPPED_UNREPORTED)
