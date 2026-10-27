from journal.events.listener import Listener
from journal.events.rows.row_event import RowEvent
from journal.events.rows.task_edited import TaskEdited
from journal.events.rows.task_closed import TaskClosed
from journal.features.workers.support.worker_actions import WorkerActions
from journal.models.proof_state import ProofState
from journal.repositories.proofs import Proofs
from journal.repositories.tasks import Tasks
from journal.repositories.workers import Workers
from journal.support.actor import Actor
from journal.support.actor_type import ActorType

RELEASING = ("completed", "cancelled")
PAUSED, BLOCKED = "paused", "blocked"
DROPPING_ACTORS = (ActorType.USER, ActorType.PHONE, ActorType.AGENT)
DROPPED_LINE = "task {task} was paused while you worked on it and is no longer yours: leave it, keep what you committed on your branch, and go on with your queue"


class WorkerTaskChanges(Listener[RowEvent]):
    """What the user does to a worker's task reaches the worker's rows: a task done or cancelled is let go by its worker, which is released once it holds no other task, a task the user or the agent paused under its worker, by force, is let go too and the worker is told in its session to go on with its queue, a blocked task waiting in a worker's queue leaves the queue and is offered again once it opens, and a title or brief written anew marks the proofs of its changed points stale and, for a worker that is not running, is kept on its row to be said with its next job."""

    def __init__(self, tasks: Tasks, workers: Workers, proofs: Proofs, actions: WorkerActions) -> None:
        self.tasks, self.workers, self.proofs, self.actions = tasks, workers, proofs, actions

    def handle(self, event: RowEvent) -> None:
        if isinstance(event, TaskClosed) and event.outcome in RELEASING:
            self.released(event)
        if isinstance(event, TaskClosed) and event.outcome == PAUSED and Actor.parse(event.actor).actor_type in DROPPING_ACTORS:
            self.dropped(event)
        if isinstance(event, TaskClosed) and event.outcome == BLOCKED:
            self.tasks.unqueued_task(self.tasks.find(event.task_id), Actor.system())
        if isinstance(event, TaskEdited):
            self.edited(event)

    def released(self, event: TaskClosed) -> None:
        holder = self.tasks.holder(self.tasks.find(event.task_id))
        if holder is None or holder.type != "workers":
            return
        self.tasks.release_task(holder, event.task_id, Actor.system())
        if not self.tasks.holder_task_ids(holder):
            self.workers.save(self.workers.find(holder.id).released(event.time), Actor.system())

    def dropped(self, event: TaskClosed) -> None:
        task = self.tasks.find(event.task_id)
        holder = self.tasks.holder(task) if task.delegated else None
        if holder is None or holder.type != "workers":
            return
        self.released(event)
        worker = self.workers.find(holder.id)
        if not self.actions.notify_refusal(worker):
            self.actions.notified(worker, DROPPED_LINE.format(task=event.task_id), "the journal", Actor.system())

    def edited(self, event: TaskEdited) -> None:
        task = self.tasks.find(event.task_id)
        for proof in self.proofs.changed_point_proofs(task, event.points):
            self.proofs.save(proof.with_(state=ProofState.STALE), Actor.system())
        holder = self.tasks.holder(task)
        if holder is not None and holder.type == "workers" and not (worker := self.workers.find(holder.id)).is_running():
            self.workers.save(worker.with_(edited_task=task.id), Actor.system())
