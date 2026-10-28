from journal.engine.states.void import Void
from journal.features.workers.states.working_task import WorkingTask
from journal.features.workers.workers_nudges import WorkersNudges
from journal.models.support.worker_silence import DISPATCHER_SPAN_SHARE
from journal.models.worker import SILENCE
from journal.models.worker_state import WorkerState
from journal.features.workers.workers_options import BUILDER_MODE
from tests.stories.builder.story_marks import story
from tests.stories.fixtures.worker.silent_worker import SilentWorker
from tests.stories.fixtures.worker.worker_delivered import WorkerDelivered

DISPATCHER_SECONDS = SILENCE.amount * DISPATCHER_SPAN_SHARE


@story(SilentWorker, mode=BUILDER_MODE)
def test_a_worker_is_told_to_log_once_in_a_quiet_span(story):
    story.agent_is_quiet_past(0)
    story.expect_agent_not_told(WorkersNudges.WORKER_LOG_DUE)
    story.expect_worker(story.start.worker, state=WorkerState.READY)
    story.expect_stack(Void, WorkingTask)


@story(WorkerDelivered, mode=BUILDER_MODE)
def test_a_worker_that_clocked_out_is_never_called_quiet(story):
    story.agent_is_quiet_past(SILENCE.amount)
    story.expect_agent_not_told(WorkersNudges.WORKER_LOG_DUE)
    story.expect_main_not_told(WorkersNudges.SILENT_WORKER)
    story.expect_worker(story.start.worker, state=WorkerState.DELIVERED)
    story.expect_stack(Void)
