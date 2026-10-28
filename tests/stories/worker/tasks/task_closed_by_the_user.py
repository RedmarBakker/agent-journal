from journal.engine.states.void import Void
from journal.features.workers.workers_nudges import WorkersNudges
from journal.models.worker_state import WorkerState
from journal.features.workers.workers_options import BUILDER_MODE
from tests.stories.builder.story_marks import story
from tests.stories.fixtures.worker.working_worker import WorkingWorker


@story(WorkingWorker, mode=BUILDER_MODE)
def test_the_user_completing_a_workers_task_releases_the_worker_and_tells_it_to_stop(story):
    story.user_completes_task(story.start.briefed, "done by hand")
    story.expect_worker(story.start.worker, state=WorkerState.RELEASED)
    story.expect_agent_told(WorkersNudges.USER_CLOSURE, task=story.start.briefed)
    story.expect_stack(Void)
