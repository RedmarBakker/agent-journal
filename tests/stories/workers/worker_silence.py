from journal.features.tasks.states.external_wait import ExternalWait
from journal.features.tasks.states.ready import Ready
from journal.features.workers.workers_nudges import WorkersNudges
from journal.models.support.worker_silence import DISPATCHER_SPAN_SHARE
from journal.models.worker import SILENCE
from tests.stories.builder.story_marks import story
from tests.stories.fixtures.clocked_in_worker import ClockedInWorker
from tests.stories.fixtures.worker_delivered import WorkerDelivered

DISPATCHER_EXTRA_SECONDS = SILENCE.amount * (DISPATCHER_SPAN_SHARE - 1)


@story(ClockedInWorker, end=[Ready, ExternalWait])
def test_a_worker_quiet_for_its_span_is_told_to_log_and_its_dispatcher_is_not_told_yet(story):
    story.worker_is_quiet_past(SILENCE.amount)
    story.expect_agent_told(WorkersNudges.WORKER_LOG_DUE)
    story.expect_agent_not_told(WorkersNudges.SILENT_WORKER)


@story(ClockedInWorker, end=[Ready, ExternalWait])
def test_the_dispatcher_is_told_of_a_worker_quiet_half_as_long_again(story):
    story.worker_is_quiet_past(SILENCE.amount)
    story.worker_is_quiet_past(DISPATCHER_EXTRA_SECONDS)
    story.expect_agent_told(WorkersNudges.SILENT_WORKER, n=story.start.worker)


@story(ClockedInWorker, end=[Ready, ExternalWait])
def test_a_worker_is_told_to_log_once_in_a_quiet_span(story):
    story.worker_is_quiet_past(SILENCE.amount)
    story.worker_is_quiet_past(0)
    story.expect_agent_not_told(WorkersNudges.WORKER_LOG_DUE)
    story.expect_agent_not_told(WorkersNudges.SILENT_WORKER)


@story(ClockedInWorker, end=[Ready, ExternalWait])
def test_a_proof_by_the_worker_starts_a_new_quiet_span(story):
    story.worker_is_quiet_past(SILENCE.amount)
    story.worker_proves(story.start.worker, 1, "parser.py:12, test_reads passes")
    story.worker_is_quiet_past(DISPATCHER_EXTRA_SECONDS)
    story.expect_agent_not_told(WorkersNudges.SILENT_WORKER)
    story.expect_agent_not_told(WorkersNudges.WORKER_LOG_DUE)


@story(WorkerDelivered, end=[Ready])
def test_a_worker_that_clocked_out_is_never_called_quiet(story):
    story.worker_is_quiet_past(SILENCE.amount)
    story.expect_agent_not_told(WorkersNudges.WORKER_LOG_DUE)
    story.expect_agent_not_told(WorkersNudges.SILENT_WORKER)
