from journal.features.plans.plans_nudges import PlansNudges
from journal.features.tasks.states.external_wait import ExternalWait
from journal.features.tasks.states.ready import Ready
from journal.features.workers.workers_nudges import WorkersNudges
from journal.models.plan_state import PlanState
from journal.models.task_state import TaskState
from journal.models.worker_state import WorkerState
from tests.stories.builder.story_marks import story
from tests.stories.fixtures.plan_approved import PlanApproved
from tests.stories.fixtures.plan_worker import PlanWorker
from tests.stories.fixtures.plan_worker_delivered import PlanWorkerDelivered


@story(PlanWorker, end=[Ready, ExternalWait])
def test_a_worker_on_a_plan_goes_on_to_the_next_task_without_reporting(story):
    story.worker_proves(story.start.worker, 1, "first.py:3, test_first passes")
    story.worker_clocks_out(story.start.worker, "the first is done")
    story.expect_agent_not_told(WorkersNudges.WORK_READY)
    story.expect_worker(story.start.worker, state=WorkerState.READY)
    story.expect_task(story.start.second_task, state=TaskState.STARTED)


@story(PlanWorkerDelivered, end=[Ready])
def test_each_task_checked_and_the_worker_merged_finishes_the_plan(story):
    story.agent_runs(f"worker check {story.start.worker} 1 --task {story.start.first_task}")
    story.agent_runs(f"worker check {story.start.worker} 1 --task {story.start.second_task}")
    story.agent_runs(f"worker merge {story.start.worker}")
    story.expect_command_passed()
    story.expect_worker(story.start.worker, state=WorkerState.MERGED)
    story.expect_plan(story.start.plan, state=PlanState.FINISHED)
    story.expect_agent_told(PlansNudges.PLAN_FINISHED, n=story.start.plan)


@story(PlanApproved, end=[Ready, ExternalWait])
def test_a_worker_on_a_plan_that_reports_after_each_task_reports_after_the_first(story):
    story.agent_runs(f"worker dispatch 'Lady Lovelace' --plan {story.start.plan} --changes 'the files of its tasks' --profile journal-medior --model sonnet --tests 'Scoped tests' --report each")
    worker = story.created_number("worker")
    story.worker_clocks_in(worker)
    story.worker_proves(worker, 1, "first.py:3, test_first passes")
    story.worker_clocks_out(worker, "the first is done")
    story.expect_agent_told(WorkersNudges.WORK_READY)
    story.expect_worker(worker, state=WorkerState.DELIVERED)


@story(PlanWorker, end=[Ready, ExternalWait])
def test_a_queued_task_the_user_cancels_leaves_the_queue(story):
    story.user_cancels_task(story.start.second_task, "not needed")
    story.worker_proves(story.start.worker, 1, "first.py:3, test_first passes")
    story.worker_clocks_out(story.start.worker, "the first is done")
    story.expect_agent_told(WorkersNudges.WORK_READY)
    story.expect_worker(story.start.worker, state=WorkerState.DELIVERED)
    story.expect_task(story.start.second_task, state=TaskState.CANCELLED)


@story(PlanWorker, end=[Ready, ExternalWait])
def test_a_queued_task_that_is_blocked_ends_the_queue_with_a_report(story):
    story.agent_runs(f"task block {story.start.second_task} 'waits on the designer'")
    story.worker_proves(story.start.worker, 1, "first.py:3, test_first passes")
    story.worker_clocks_out(story.start.worker, "the first is done")
    story.expect_agent_told(WorkersNudges.WORK_READY)
    story.expect_task(story.start.second_task, state=TaskState.BLOCKED)
