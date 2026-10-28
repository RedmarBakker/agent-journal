from journal.engine.safety_conduct import PANIC_REFUSAL_COUNT
from journal.engine.states.void import Void
from journal.features.workers.states.working_task import WorkingTask
from journal.features.workers.workers_options import BUILDER_MODE
from journal.models.worker_state import WorkerState
from journal.support.agent_role import AgentRole
from tests.stories.builder.story_marks import story
from tests.stories.fixtures.worker.dispatched_worker import DispatchedWorker
from tests.stories.fixtures.worker.working_worker import WorkingWorker


@story(DispatchedWorker, mode=BUILDER_MODE, scope=AgentRole.WORKER)
def test_a_worker_stopping_again_and_again_on_its_floor_never_panics(story):
    for _ in range(PANIC_REFUSAL_COUNT + 1):
        story.agent_stops()
    story.expect_allowed()
    story.expect_worker(story.start.worker, state=WorkerState.DISPATCHED)
    story.expect_stack(Void)
