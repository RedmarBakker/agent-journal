from journal.events.rows.released_tasks import ReleasedTasks
from journal.features.tasks.states.ready import Ready
from journal.features.tasks.tasks_nudges import TasksNudges
from journal.features.workers.workers_nudges import WorkersNudges
from journal.models.plan_state import PlanState
from journal.models.task_state import TaskState
from journal.models.worker_state import WorkerState
from journal.support.agent_role import AgentRole
from tests.stories.builder.story_marks import story
from tests.stories.fixtures.worker.plan_worker import PlanWorker
from tests.stories.fixtures.worker.worker_delivered import WorkerDelivered
from tests.stories.fixtures.worker.working_worker import WorkingWorker


@story(WorkingWorker, subject=AgentRole.MAIN)
def test_the_user_cancelling_a_workers_task_leaves_it_cancelled_and_undelegated(story):
    story.user_cancels_task(story.tasks.briefed, "not needed")
    story.expect_task(story.tasks.briefed, state=TaskState.CANCELLED)
    story.expect_worker(story.agents.workers.first(), state=WorkerState.RELEASED)
    story.expect_stack(story.agents.subject, Ready)


@story(WorkingWorker, subject=AgentRole.MAIN)
def test_the_user_blocking_a_workers_task_takes_it_from_the_worker(story):
    story.user_blocks_task(story.tasks.briefed, "later")
    story.expect_task(story.tasks.briefed, state=TaskState.BLOCKED)
    story.expect_worker(story.agents.workers.first(), state=WorkerState.RELEASED)
    story.expect_stack(story.agents.subject, Ready)


@story(PlanWorker, subject=AgentRole.MAIN)
def test_a_whole_plan_waits_for_its_workers_stop_then_returns_its_open_tasks(story):
    worker = story.agents.workers.first()
    number = worker.number
    result = story.agent_runs(story.agents.subject, f"worker release {worker}")
    result.expect_command_refused()
    story.agent_runs(story.agents.subject, f"worker stop {worker}")
    result = story.agent_runs(story.agents.subject, f"worker release {worker}")
    result.expect_command_passed()
    released = ReleasedTasks(number, (story.tasks.first, story.tasks.second), story.plans.first)
    result.expect_agent_told(story.agents.subject, TasksNudges.TASKS_RELEASED, tasks=released.subject(), worker=number, them="them")
    result.expect_agent_not_told(story.agents.subject, TasksNudges.TASK_REOPENED)
    story.expect_plan(story.plans.first, state=PlanState.PAUSED)
    story.expect_task(story.tasks.first, delegated=False)
    story.expect_task(story.tasks.second, state=TaskState.OPEN, delegated=False)
    story.expect_worker(worker, state=WorkerState.RELEASED)
    story.expect_stack(story.agents.subject, Ready)


@story(WorkerDelivered, subject=AgentRole.MAIN)
def test_a_task_the_user_cancels_while_its_work_waits_releases_the_worker_unmerged(story):
    story.user_cancels_task(story.tasks.briefed, "not needed")
    story.expect_worker(story.agents.workers.first(), state=WorkerState.RELEASED)
    story.expect_task(story.tasks.briefed, state=TaskState.CANCELLED)
    story.expect_stack(story.agents.subject, Ready)


@story(WorkingWorker, subject=AgentRole.MAIN)
def test_stopping_a_worker_tells_the_agent_it_ended_without_a_report(story):
    result = story.agent_runs(story.agents.subject, f"worker stop {story.agents.workers.first()}")
    result.expect_command_passed()
    story.expect_worker(story.agents.workers.first(), state=WorkerState.STOPPED)
    result.expect_agent_told(story.agents.subject, WorkersNudges.WORKER_STOPPED_UNREPORTED)
    story.expect_stack(story.agents.subject, Ready)
