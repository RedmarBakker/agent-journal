from typing import ClassVar

from journal.features.workers.session_workers_part import SessionWorkersPart
from journal.features.workers.support.session_workers_data import SessionWorkersData
from journal.models.agent import Agent
from journal.models.support.ref import Ref
from journal.repositories.command_outputs import CommandOutputs
from journal.repositories.tasks import Tasks
from journal.repositories.worker_todos import WorkerTodos
from journal.repositories.workers import Workers
from journal.support.actor import Actor


class SessionWorkersReader:
    """Reads, for a helper's session, the worker rows it runs as, the outputs they left running and the to-do items of their tasks."""

    source: ClassVar[type[SessionWorkersPart]] = SessionWorkersPart

    def __init__(self, workers: Workers, outputs: CommandOutputs, tasks: Tasks, todos: WorkerTodos) -> None:
        self.workers, self.outputs, self.tasks, self.todos = workers, outputs, tasks, todos

    def read(self, agent: Agent) -> SessionWorkersData:
        rows = tuple(self.workers.session_worker(agent.session))
        unfinished = tuple(output.row_id for worker in rows for output in self.outputs.unfinished(Actor.worker(worker.id)))
        todos = tuple(item for worker in rows for task_id in self.tasks.holder_task_ids(Ref.build(worker)) for item in self.todos.task_items(self.tasks.find(task_id)))
        return SessionWorkersData(rows, todos, unfinished)
