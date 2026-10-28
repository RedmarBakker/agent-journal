from journal.features.tasks.states.external_wait import ExternalWait
from journal.features.tasks.states.ready import Ready
from journal.features.workers.workers_options import BUILDER_MODE
from journal.models.worker_state import WorkerState
from tests.stories.builder.story_marks import story
from tests.stories.fixtures.worker.working_worker import WorkingWorker


@story(WorkingWorker, mode=BUILDER_MODE)
def test_a_rebase_of_a_worker_out_on_a_task_waits_for_its_next_clock_out(story):
    story.agent_runs(f"worker rebase {story.start.worker}")
    story.expect_command_passed()
    story.expect_command_text("rebased at its next clock-out")
    story.expect_worker(story.start.worker, state=WorkerState.READY)
    story.expect_stack(Ready, ExternalWait)
