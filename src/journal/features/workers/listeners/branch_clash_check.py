from functools import partial

from journal.events.listener import Listener
from journal.events.rows.worker_merged import WorkerMerged
from journal.features.workers.support.clash_return import ClashReturn
from journal.features.workers.support.worker_branch import WorkerBranch
from journal.repositories.scope import Scope
from journal.repositories.workers import Workers
from journal.support.listener_queue import ListenerQueue


class BranchClashCheck(Listener[WorkerMerged]):
    """When a merge lands, every other worker whose clocked-out work waits to be checked and merged has its branch checked against the new head without touching it, on the deferred worker; one that now clashes is sent back to rebase before anyone tries to merge it."""

    def __init__(self, deferred: ListenerQueue, workers: Workers, branch: WorkerBranch, clashes: ClashReturn, scope: Scope) -> None:
        self.deferred, self.workers, self.branch, self.clashes, self.scope = deferred, workers, branch, clashes, scope

    def handle(self, event: WorkerMerged) -> None:
        self.deferred.add(partial(self.checked, event))

    def checked(self, event: WorkerMerged) -> None:
        with self.scope.environment(event.environment_id):
            for worker in self.workers.checkable_workers():
                clashing = self.branch.clash_preview(worker) if worker.worktree and worker.id != event.worker.id else ""
                if clashing:
                    self.clashes.send(worker, clashing)
