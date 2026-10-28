from journal.features.tasks.states.external_wait import ExternalWait
from journal.features.tasks.states.ready import Ready
from journal.models.task_state import TaskState
from journal.models.worker_state import WorkerState
from journal.features.workers.workers_options import BUILDER_MODE
from tests.stories.builder.story_marks import story
from tests.stories.fixtures.worker.plan_worker_delivered import PlanWorkerDelivered
from tests.stories.fixtures.worker.worker_delivered import WorkerDelivered
from tests.stories.fixtures.worker.working_worker import WorkingWorker


@story(WorkerDelivered, mode=BUILDER_MODE)
def test_checked_proofs_let_the_work_be_merged(story):
    story.agent_runs(f"worker check {story.start.worker} 1")
    story.agent_runs(f"worker check {story.start.worker} 2")
    story.agent_runs(f"worker merge {story.start.worker}")
    story.expect_command_passed()
    story.expect_task(story.start.briefed, state=TaskState.COMPLETED)
    story.expect_stack(Ready)


@story(WorkerDelivered, mode=BUILDER_MODE)
def test_a_merge_with_an_unchecked_point_is_refused(story):
    story.agent_runs(f"worker merge {story.start.worker}")
    story.expect_command_refused()
    story.expect_worker(story.start.worker, state=WorkerState.DELIVERED)
    story.expect_task(story.start.briefed, delegated=True)
    story.expect_stack(Ready)


@story(WorkingWorker, mode=BUILDER_MODE)
def test_a_merge_of_a_worker_that_has_not_clocked_out_is_refused(story):
    story.agent_runs(f"worker merge {story.start.worker}")
    story.expect_command_refused()
    story.expect_worker(story.start.worker, state=WorkerState.READY)
    story.expect_stack(Ready, ExternalWait)


@story(WorkingWorker, mode=BUILDER_MODE)
def test_merging_every_waiting_worker_with_none_waiting_is_refused(story):
    story.agent_runs("worker merge --all")
    story.expect_command_refused()
    story.expect_worker(story.start.worker, state=WorkerState.READY)
    story.expect_stack(Ready, ExternalWait)


@story(PlanWorkerDelivered, mode=BUILDER_MODE)
def test_a_worker_whose_finished_queue_waits_to_be_merged_is_released_only_with_drop(story):
    story.agent_runs(f"worker release {story.start.worker}")
    story.expect_command_refused()
    story.agent_runs(f"worker release {story.start.worker} --drop")
    story.expect_command_passed()
    story.expect_task(story.start.first_task, delegated=False)
    story.expect_stack(Ready)
