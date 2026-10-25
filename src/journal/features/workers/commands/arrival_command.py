from argparse import Namespace
from datetime import datetime, timezone

from journal.console.command import WORKER_KINDS, Command
from journal.models.support.ref import Ref
from journal.models.task_state import TaskState
from journal.models.worker import Worker
from journal.models.worker_state import WorkerState
from journal.repositories.tasks import Tasks
from journal.features.workers.support.pool_worker_moves import READY, PoolWorkerMoves
from journal.repositories.workers import Workers
from journal.support.caller import Caller
from journal.support.rejection import Rejection


class ArrivalCommand(Command):
    """journal clock-in: a worker says it is ready, which keeps the task it holds delegated to it and tells the agent that dispatched it."""

    noun = "clock-in"
    default_verb = "record"
    callers = {"record": WORKER_KINDS}

    def __init__(self, workers: Workers, tasks: Tasks, moves: PoolWorkerMoves) -> None:
        self.workers, self.tasks, self.moves = workers, tasks, moves

    def arguments(self, verbs) -> None:
        self.verb(verbs, "record", "say you are ready: your task is started under you")

    def record(self, args: Namespace, caller: Caller) -> int:
        if caller.worker_number is None:
            raise Rejection("only a worker clocks in: a worker's commands carry its number")
        worker = self.workers.find(caller.worker_number)
        if worker.state != WorkerState.DISPATCHED:
            raise Rejection(f"worker {worker.id} is {worker.state}: a worker clocks in once each time it is sent")
        holdings = self.tasks.holder_task_ids(Ref(Worker.table(), worker.id))
        if not holdings:
            raise Rejection(f"worker {worker.id} holds no task: a worker clocks in on the task it was sent on")
        moment, task = datetime.now(timezone.utc), self.tasks.find(holdings[0])
        if not task.delegated:
            task = self.tasks.save(task.delegate(moment), caller.actor)
        if task.state != TaskState.STARTED:
            self.tasks.save(task.worker_started(moment), caller.actor)
        if self.moves.is_remote(worker):
            self.moves.ask(worker, READY, {}, caller.actor)
        else:
            self.workers.save(worker.ready(moment.timestamp()), caller.actor)
        print(f"worker {worker.id} clocked in on task {task.id}: {task.title}")
        return 0
