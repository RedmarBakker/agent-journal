from journal.features.tasks.states.external_wait import ExternalWait
from journal.features.tasks.states.ready import Ready
from journal.models.task_state import TaskState
from journal.models.worker_state import WorkerState
from journal.support.agent_role import AgentRole
from tests.stories.builder.story_marks import story
from tests.stories.fixtures.worker.plan_worker_delivered import PlanWorkerDelivered
from tests.stories.fixtures.worker.worker_delivered import WorkerDelivered
from tests.stories.fixtures.worker.working_worker import WorkingWorker


@story(WorkerDelivered, subject=AgentRole.MAIN)
def test_checked_proofs_let_the_work_be_merged(story):
    story.agent_runs(story.agents.subject, f"worker check {story.agents.workers.first()} 1")
    story.agent_runs(story.agents.subject, f"worker check {story.agents.workers.first()} 2")
    result = story.agent_runs(story.agents.subject, f"worker merge {story.agents.workers.first()}")
    result.expect_command_passed()
    story.expect_task(story.tasks.briefed, state=TaskState.COMPLETED)
    story.expect_stack(story.agents.subject, Ready)


@story(WorkerDelivered, subject=AgentRole.MAIN)
def test_a_merge_with_an_unchecked_point_is_refused(story):
    result = story.agent_runs(story.agents.subject, f"worker merge {story.agents.workers.first()}")
    result.expect_command_refused()
    story.expect_worker(story.agents.workers.first(), state=WorkerState.DELIVERED)
    story.expect_task(story.tasks.briefed, delegated=True)
    story.expect_stack(story.agents.subject, Ready)


@story(WorkingWorker, subject=AgentRole.MAIN)
def test_a_merge_of_a_worker_that_has_not_clocked_out_is_refused(story):
    result = story.agent_runs(story.agents.subject, f"worker merge {story.agents.workers.first()}")
    result.expect_command_refused()
    story.expect_worker(story.agents.workers.first(), state=WorkerState.READY)
    story.expect_stack(story.agents.subject, Ready, ExternalWait)


@story(WorkingWorker, subject=AgentRole.MAIN)
def test_merging_every_waiting_worker_with_none_waiting_is_refused(story):
    result = story.agent_runs(story.agents.subject, "worker merge --all")
    result.expect_command_refused()
    story.expect_worker(story.agents.workers.first(), state=WorkerState.READY)
    story.expect_stack(story.agents.subject, Ready, ExternalWait)


@story(PlanWorkerDelivered, subject=AgentRole.MAIN)
def test_a_worker_whose_finished_queue_waits_to_be_merged_is_released_only_with_drop(story):
    result = story.agent_runs(story.agents.subject, f"worker release {story.agents.workers.first()}")
    result.expect_command_refused()
    result = story.agent_runs(story.agents.subject, f"worker release {story.agents.workers.first()} --drop")
    result.expect_command_passed()
    story.expect_task(story.tasks.first, delegated=False)
    story.expect_stack(story.agents.subject, Ready)
