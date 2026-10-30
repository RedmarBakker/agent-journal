from argparse import Namespace
from datetime import datetime, timezone

from journal.console.command import Command
from journal.models.support.ref import Ref
from journal.models.worker import Worker
from journal.repositories.tasks import Tasks
from journal.repositories.workers import Workers
from journal.support.caller import Caller
from journal.support.rejection import Rejection
from journal.support.time_source import TimeSource


class ArrivalCommand(Command):
    """journal clock-in: a worker says it is ready, which keeps the task it holds delegated to it and tells the agent that dispatched it."""

    noun = "clock-in"
    default_verb = "record"

    def __init__(self, workers: Workers, tasks: Tasks, time_source: TimeSource) -> None:
        self.time_source = time_source
        self.workers, self.tasks = workers, tasks

    def arguments(self, verbs) -> None:
        self.verb(verbs, "record", "say you are ready: your task is started under you")

    def record(self, args: Namespace, caller: Caller) -> int:
        worker = self.workers.find(caller.worker_number)
        if not worker.is_dispatched():
            raise Rejection(f"worker {worker.id} is {worker.state}: a worker clocks in once each time it is sent")
        holdings = self.tasks.holder_task_ids(Ref(Worker.table(), worker.id))
        if not holdings:
            raise Rejection(f"worker {worker.id} has no task: a worker clocks in on the task it was sent on")
        moment, task = self.time_source.moment(), self.tasks.find(holdings[0])
        if not task.delegated:
            task = self.tasks.save(task.delegate(moment), caller.actor)
        if not task.is_started():
            self.tasks.save(task.worker_started(moment), caller.actor)
        self.workers.save(worker.ready(moment.timestamp()), caller.actor)
        print(f"worker {worker.id} clocked in on task {task.id}: {task.title}")
        return 0
