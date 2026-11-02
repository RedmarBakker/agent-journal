import threading

from journal.events.bus import Bus
from journal.events.moments.worker_work_merged import WorkerWorkMerged
from journal.events.rows.worker_mention import WorkerMention
from journal.events.rows.worker_released import WorkerReleased
from tests.stories.builder.worker_merge_wait import WorkerMergeWait


def test_a_worker_release_during_a_background_merge_does_not_finish_the_merge_wait():
    bus = Bus()
    waiter = WorkerMergeWait(bus, 17)
    waiting = threading.Event()
    returned = threading.Event()
    released = threading.Event()
    finish_merge = threading.Event()

    def wait_for_merge():
        waiting.set()
        waiter.wait()
        returned.set()

    def merge_in_background():
        bus.dispatch(WorkerReleased(
            environment_id=1, time=0, row_id=17, actor="system", ref="workers:17",
            worker=WorkerMention(id=17, name="Ada", dispatcher=None),
        ))
        released.set()
        finish_merge.wait(5)
        bus.dispatch(WorkerWorkMerged(
            environment_id=1, worker=17, name="Ada", dispatcher=None, task=23, next_task=0, time=0,
        ))

    waiting_thread = threading.Thread(target=wait_for_merge, name="wait-for-worker-merge", daemon=True)
    merge_thread = threading.Thread(target=merge_in_background, name="worker-merge", daemon=True)
    waiting_thread.start()
    assert waiting.wait(5), "the story started waiting for the merge event"
    merge_thread.start()
    assert released.wait(5), "the worker release raced the background merge"
    assert not returned.is_set(), "a release does not complete the merge wait"
    finish_merge.set()
    merge_thread.join(5)
    waiting_thread.join(5)
    assert not merge_thread.is_alive(), "the merge event was delivered"
    assert not waiting_thread.is_alive(), "the merge wait returned"
    assert returned.is_set(), "the story continued after the worker merge event"
