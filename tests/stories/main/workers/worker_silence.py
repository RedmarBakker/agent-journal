from journal.features.tasks.states.external_wait import ExternalWait
from journal.features.tasks.states.ready import Ready
from journal.features.workers.workers_nudges import WorkersNudges
from journal.models.support.worker_silence import DISPATCHER_SPAN_SHARE
from journal.models.worker import SILENCE
from journal.features.workers.workers_options import BUILDER_MODE
from tests.stories.builder.story_marks import story
from tests.stories.fixtures.worker.silent_worker import SilentWorker

DISPATCHER_SECONDS = SILENCE.amount * DISPATCHER_SPAN_SHARE


@story(SilentWorker, mode=BUILDER_MODE)
def test_the_dispatcher_is_told_of_a_worker_quiet_half_as_long_again(story):
    story.worker_is_quiet_past(DISPATCHER_SECONDS)
    story.expect_agent_told(WorkersNudges.SILENT_WORKER, n=story.start.worker)
    story.expect_stack(Ready, ExternalWait)


@story(SilentWorker, mode=BUILDER_MODE)
def test_a_proof_by_the_worker_starts_a_new_quiet_span(story):
    story.worker_proves(story.start.worker, 1, "parser.py:12, test_reads passes")
    story.worker_is_quiet_past(DISPATCHER_SECONDS)
    story.expect_agent_not_told(WorkersNudges.SILENT_WORKER)
    story.expect_task(story.start.briefed, delegated=True)
    story.expect_stack(Ready, ExternalWait)
