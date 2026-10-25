from journal.events.listener import Listener
from journal.events.rows.row_event import RowEvent
from journal.events.rows.task_edited import TaskEdited
from journal.events.rows.task_closed import TaskClosed
from journal.models.proof_state import ProofState
from journal.repositories.proofs import Proofs
from journal.repositories.tasks import Tasks
from journal.repositories.workers import Workers
from journal.support.actor import Actor

RELEASING = ("completed", "cancelled")


class WorkerTaskChanges(Listener[RowEvent]):
    """What the user does to a worker's task reaches the worker's rows: a task done or cancelled is let go by its worker, which is released once it holds no other task, and a title or brief written anew marks the proofs of its changed points stale and, for a worker that is not running, is kept on its row to be said with its next job."""

    def __init__(self, tasks: Tasks, workers: Workers, proofs: Proofs) -> None:
        self.tasks, self.workers, self.proofs = tasks, workers, proofs

    def handle(self, event: RowEvent) -> None:
        if isinstance(event, TaskClosed) and event.outcome in RELEASING:
            self.released(event)
        if isinstance(event, TaskEdited):
            self.edited(event)

    def released(self, event: TaskClosed) -> None:
        holder = self.tasks.holder(self.tasks.find(event.task_id))
        if holder is None or holder.type != "workers":
            return
        self.tasks.release_task(holder, event.task_id, Actor.system())
        if not self.tasks.holder_task_ids(holder):
            self.workers.save(self.workers.find(holder.id).released(event.time), Actor.system())

    def edited(self, event: TaskEdited) -> None:
        task = self.tasks.find(event.task_id)
        for proof in self.proofs.changed_point_proofs(task, event.points):
            self.proofs.save(proof.with_(state=ProofState.STALE), Actor.system())
        holder = self.tasks.holder(task)
        if holder is not None and holder.type == "workers" and not (worker := self.workers.find(holder.id)).is_running():
            self.workers.save(worker.with_(edited_task=task.id), Actor.system())
