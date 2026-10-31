from journal.events.listener import Listener
from journal.events.moments.worker_work_merged import WorkerWorkMerged
from journal.repositories.scope import Scope
from journal.repositories.task_outcomes import TaskOutcomes
from journal.support.listener_queue import ListenerQueue


class TaskOutcomeMerges(Listener[WorkerWorkMerged]):
    """Records accepted worker merges before policy-specific delivery evidence is admitted."""

    def __init__(self, deferred: ListenerQueue, outcomes: TaskOutcomes, scope: Scope) -> None:
        self.deferred, self.outcomes, self.scope = deferred, outcomes, scope

    def handle(self, event: WorkerWorkMerged) -> None:
        self.deferred.add(lambda: self.record(event))

    def record(self, event: WorkerWorkMerged) -> None:
        with self.scope.environment(event.environment_id):
            self.outcomes.record_merge(event)
