from journal.features.tasks.states.external_wait import ExternalWait
from journal.features.tasks.states.ready import Ready
from journal.features.workers.workers_nudges import WorkersNudges
from journal.models.plan_state import PlanState
from journal.models.task_state import TaskState
from journal.models.worker_state import WorkerState
from journal.features.workers.workers_options import BUILDER_MODE
from journal.support.agent_role import AgentRole
from tests.stories.builder.story_marks import story
from tests.stories.fixtures.main.plan_approved import PlanApproved
from tests.stories.fixtures.worker.plan_worker import PlanWorker
from tests.stories.fixtures.worker.plan_worker_delivered import PlanWorkerDelivered


@story(PlanWorker, mode=BUILDER_MODE, subject=AgentRole.MAIN)
def test_a_worker_on_a_plan_goes_on_to_the_next_task_without_reporting(story):
    story.agent_proves(story.agents.workers.first(), 1, "first.py:3, test_first passes")
    story.agent_clocks_out(story.agents.workers.first(), "the first is done")
    story.expect_agent_not_told(story.agents.subject, WorkersNudges.WORK_READY)
    story.expect_worker(story.agents.workers.first(), state=WorkerState.READY)
    story.expect_task(story.fixture.second_task, delegated=True)
    story.expect_stack(story.agents.subject, Ready, ExternalWait)


@story(PlanWorkerDelivered, mode=BUILDER_MODE, subject=AgentRole.MAIN)
def test_each_task_checked_and_the_worker_merged_finishes_the_plan(story):
    story.agent_runs(story.agents.subject, f"worker check {story.agents.workers.first()} 1 --task {story.fixture.first_task}")
    story.agent_runs(story.agents.subject, f"worker check {story.agents.workers.first()} 1 --task {story.fixture.second_task}")
    story.agent_runs(story.agents.subject, f"worker merge {story.agents.workers.first()}")
    story.expect_command_passed()
    story.expect_worker(story.agents.workers.first(), state=WorkerState.MERGED)
    story.expect_plan(story.fixture.plan, state=PlanState.FINISHED)
    story.expect_agent_told(story.agents.subject, WorkersNudges.IDLE_WORKER, n=story.agents.workers.first())
    story.expect_stack(story.agents.subject, Ready)


@story(PlanApproved, mode=BUILDER_MODE, subject=AgentRole.MAIN)
def test_a_worker_on_a_plan_that_reports_after_each_task_reports_after_the_first(story):
    story.agent_runs(story.agents.subject, f"worker dispatch 'Lady Lovelace' --plan {story.fixture.plan} --changes 'the files of its tasks' --profile journal-medior --model sonnet --tests 'Scoped tests' --report each")
    worker = story.created_number("worker")
    story.agent_starts_a_session(story.agents.workers.get(worker))
    story.agent_clocks_in(story.agents.workers.get(worker))
    story.agent_proves(story.agents.workers.get(worker), 1, "first.py:3, test_first passes")
    story.agent_clocks_out(story.agents.workers.get(worker), "the first is done")
    story.expect_agent_told(story.agents.subject, WorkersNudges.WORK_READY)
    story.expect_worker(worker, state=WorkerState.DELIVERED)
    story.expect_task(story.fixture.first_task, delegated=True)
    story.expect_task(story.fixture.second_task, delegated=True)
    story.expect_stack(story.agents.subject, Ready)


@story(PlanWorker, mode=BUILDER_MODE, subject=AgentRole.MAIN)
def test_a_queued_task_the_user_cancels_leaves_the_queue(story):
    story.user_cancels_task(story.fixture.second_task, "not needed")
    story.agent_proves(story.agents.workers.first(), 1, "first.py:3, test_first passes")
    story.agent_clocks_out(story.agents.workers.first(), "the first is done")
    story.expect_agent_told(story.agents.subject, WorkersNudges.WORK_READY)
    story.expect_worker(story.agents.workers.first(), state=WorkerState.DELIVERED)
    story.expect_task(story.fixture.second_task, state=TaskState.CANCELLED)
    story.expect_stack(story.agents.subject, Ready)


@story(PlanWorker, mode=BUILDER_MODE, subject=AgentRole.MAIN)
def test_a_queued_task_that_is_blocked_ends_the_queue_with_a_report(story):
    story.agent_runs(story.agents.subject, f"task block {story.fixture.second_task} 'waits on the designer'")
    story.agent_proves(story.agents.workers.first(), 1, "first.py:3, test_first passes")
    story.agent_clocks_out(story.agents.workers.first(), "the first is done")
    story.expect_agent_told(story.agents.subject, WorkersNudges.WORK_READY)
    story.expect_task(story.fixture.second_task, state=TaskState.BLOCKED)
    story.expect_task(story.fixture.first_task, delegated=True)
    story.expect_stack(story.agents.subject, Ready)
