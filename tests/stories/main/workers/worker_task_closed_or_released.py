from journal.features.tasks.states.ready import Ready
from journal.features.workers.workers_nudges import WorkersNudges
from journal.models.task_state import TaskState
from journal.models.worker_state import WorkerState
from journal.features.workers.workers_options import BUILDER_MODE
from journal.support.agent_role import AgentRole
from tests.stories.builder.story_marks import story
from tests.stories.fixtures.worker.plan_worker import PlanWorker
from tests.stories.fixtures.worker.worker_delivered import WorkerDelivered
from tests.stories.fixtures.worker.working_worker import WorkingWorker


@story(WorkingWorker, mode=BUILDER_MODE, scope=AgentRole.MAIN)
def test_the_user_cancelling_a_workers_task_leaves_it_cancelled_and_undelegated(story):
    story.user_cancels_task(story.start.briefed, "not needed")
    story.expect_task(story.start.briefed, state=TaskState.CANCELLED)
    story.expect_worker(story.start.worker, state=WorkerState.RELEASED)
    story.expect_stack(Ready)


@story(WorkingWorker, mode=BUILDER_MODE, scope=AgentRole.MAIN)
def test_the_user_pausing_a_workers_task_takes_it_from_the_worker(story):
    story.user_pauses_task(story.start.briefed, "later")
    story.expect_task(story.start.briefed, state=TaskState.PAUSED)
    story.expect_worker(story.start.worker, state=WorkerState.RELEASED)
    story.expect_stack(Ready)


@story(PlanWorker, mode=BUILDER_MODE, scope=AgentRole.MAIN)
def test_releasing_a_worker_still_out_waits_for_its_stop_and_then_opens_its_queue(story):
    story.agent_runs(f"worker release {story.start.worker}")
    story.expect_command_refused()
    story.agent_runs(f"worker stop {story.start.worker}")
    story.agent_runs(f"worker release {story.start.worker}")
    story.expect_command_passed()
    story.expect_task(story.start.second_task, state=TaskState.OPEN, delegated=False)
    story.expect_worker(story.start.worker, state=WorkerState.RELEASED)
    story.expect_stack(Ready)


@story(WorkerDelivered, mode=BUILDER_MODE, scope=AgentRole.MAIN)
def test_a_task_the_user_cancels_while_its_work_waits_releases_the_worker_unmerged(story):
    story.user_cancels_task(story.start.briefed, "not needed")
    story.expect_worker(story.start.worker, state=WorkerState.RELEASED)
    story.expect_task(story.start.briefed, state=TaskState.CANCELLED)
    story.expect_stack(Ready)


@story(WorkingWorker, mode=BUILDER_MODE, scope=AgentRole.MAIN)
def test_stopping_a_worker_tells_the_agent_it_ended_without_a_report(story):
    story.agent_runs(f"worker stop {story.start.worker}")
    story.expect_command_passed()
    story.expect_worker(story.start.worker, state=WorkerState.STOPPED)
    story.expect_agent_told(WorkersNudges.WORKER_STOPPED_UNREPORTED)
    story.expect_stack(Ready)
