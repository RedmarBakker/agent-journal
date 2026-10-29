from dataclasses import dataclass

from journal.models.worker import Worker
from journal.models.worker_todo import WorkerTodo


@dataclass(frozen=True)
class SessionWorkersData:
    """The worker rows a helper's session runs as, the outputs they left running and the to-do items of the tasks they hold."""

    session_workers: tuple[Worker, ...] = ()
    todos: tuple[WorkerTodo, ...] = ()
    unfinished_outputs: tuple[int, ...] = ()
