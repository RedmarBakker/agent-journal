from journal.engine.states.void import Void
from journal.features.workers.states.working_task import WorkingTask
from journal.features.workers.workers_options import BUILDER_MODE
from journal.models.task_state import TaskState
from journal.models.worker_state import WorkerState
from journal.support.agent_role import AgentRole
from tests.stories.builder.story_marks import story
from tests.stories.fixtures.worker.plan_worker import PlanWorker


@story(PlanWorker, mode=BUILDER_MODE, scope=AgentRole.WORKER)
def test_a_queued_task_the_user_cancels_is_skipped_and_the_worker_delivers(story):
    story.user_cancels_task(story.start.second_task, "the second page is no longer wanted")
    story.agent_runs("proof 1 'first.py:3, test_first passes'")
    story.agent_runs("clock-out 'the first is done'")
    story.expect_worker(story.start.worker, state=WorkerState.DELIVERED)
    story.expect_task(story.start.second_task, state=TaskState.CANCELLED)
    story.expect_stack(Void)
