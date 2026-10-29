from functools import partial

from journal.events.listener import Listener
from journal.events.moments.worker_merge_clash import WorkerMergeClash
from journal.features.workers.support.clash_return import ClashReturn
from journal.repositories.scope import Scope
from journal.repositories.workers import Workers
from journal.support.listener_queue import ListenerQueue


class MergeClashReturn(Listener[WorkerMergeClash]):
    """A merge refused on a clash sends the worker's branch back to rebase, on the deferred worker once the merge has let go of it."""

    def __init__(self, deferred: ListenerQueue, workers: Workers, clashes: ClashReturn, scope: Scope) -> None:
        self.deferred, self.workers, self.clashes, self.scope = deferred, workers, clashes, scope

    def handle(self, event: WorkerMergeClash) -> None:
        self.deferred.add(partial(self.returned, event))

    def returned(self, event: WorkerMergeClash) -> None:
        with self.scope.environment(event.environment_id):
            self.clashes.send(self.workers.find(event.worker), event.clashing)
