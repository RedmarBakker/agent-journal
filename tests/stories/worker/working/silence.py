from journal.engine.states.void import Void
from journal.features.workers.states.working_task import WorkingTask
from journal.features.workers.workers_nudges import WorkersNudges
from journal.models.support.worker_silence import DISPATCHER_SPAN_SHARE
from journal.models.worker import SILENCE
from journal.models.worker_state import WorkerState
from journal.features.workers.workers_options import BUILDER_MODE
from journal.support.agent_role import AgentRole
from tests.stories.builder.story_marks import story
from tests.stories.fixtures.worker.silent_worker import SilentWorker
from tests.stories.fixtures.worker.worker_delivered import WorkerDelivered

DISPATCHER_SECONDS = SILENCE.amount * DISPATCHER_SPAN_SHARE


@story(SilentWorker, mode=BUILDER_MODE, subject=AgentRole.WORKER)
def test_a_worker_is_told_to_log_once_in_a_quiet_span(story):
    result = story.agent_is_quiet_past(story.agents.subject, 0)
    result.expect_agent_not_told(story.agents.subject, WorkersNudges.WORKER_LOG_DUE)
    story.expect_worker(story.agents.workers.first(), state=WorkerState.READY)
    story.expect_stack(story.agents.subject, Void, WorkingTask)


@story(WorkerDelivered, mode=BUILDER_MODE, subject=AgentRole.WORKER)
def test_a_worker_that_clocked_out_is_never_called_quiet(story):
    result = story.agent_is_quiet_past(story.agents.subject, SILENCE.amount)
    result.expect_agent_not_told(story.agents.subject, WorkersNudges.WORKER_LOG_DUE)
    result.expect_agent_not_told(story.agents.main, WorkersNudges.SILENT_WORKER)
    story.expect_worker(story.agents.workers.first(), state=WorkerState.DELIVERED)
    story.expect_stack(story.agents.subject, Void)
