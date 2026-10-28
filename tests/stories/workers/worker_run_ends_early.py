from journal.features.tasks.states.ready import Ready
from journal.features.workers.workers_nudges import WorkersNudges
from journal.models.worker_state import WorkerState
from tests.stories.builder.story_marks import story
from tests.stories.fixtures.clocked_in_worker import ClockedInWorker
from tests.stories.fixtures.worker_delivered import WorkerDelivered


@story(ClockedInWorker, end=[Ready])
def test_a_worker_whose_run_ends_before_it_clocks_out_with_no_session_to_ask_is_named_at_once(story):
    story.worker_run_ends(story.start.worker)
    story.expect_agent_told(WorkersNudges.RUN_UNFINISHED, n=story.start.worker)
    story.expect_worker(story.start.worker, state=WorkerState.UNFINISHED)
    story.expect_stack(Ready)


@story(WorkerDelivered, end=[Ready])
def test_a_worker_whose_run_ends_after_it_clocked_out_is_never_unfinished(story):
    story.worker_run_ends(story.start.worker)
    story.expect_agent_not_told(WorkersNudges.RUN_UNFINISHED)
    story.expect_worker(story.start.worker, state=WorkerState.DELIVERED)
