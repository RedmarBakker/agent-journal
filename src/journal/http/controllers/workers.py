from journal.features.workers.support.worker_actions import WorkerActions
from journal.features.workers.support.worker_reports import WorkerReports
from journal.http.support.request import Request
from journal.support.response import Response
from journal.http.controllers.controller import Controller
from journal.http.support.model_fields import ModelFields
from journal.features.workers.support.worker_task_view import WorkerTaskView
from journal.models.worker import Worker
from journal.repositories.agents import Agents
from journal.repositories.proofs import Proofs
from journal.repositories.tasks import Tasks
from journal.repositories.worker_todos import WorkerTodos
from journal.repositories.workers import Workers


class WorkerController(Controller[Worker]):
    """The workers sent from here; one stopped is closed. Their list carries each one's own fields; one read by id carries the last report it filed, the task it holds, the task's points, its to-do items and the latest proof of each point, and the task it worked on before. The viewer sends one its next job, stops it, retires it, checks a proof, sends one back short or merges its work, as the commands do."""

    repository: Workers

    def __init__(self, workers: Workers, reports: WorkerReports, actions: WorkerActions, tasks: Tasks, proofs: Proofs, todos: WorkerTodos, agents: Agents) -> None:
        self.repository, self.reports, self.actions, self.tasks, self.proofs, self.todos, self.agents = workers, reports, actions, tasks, proofs, todos, agents

    def check(self, request: Request) -> Response:
        self.actions.check(request.number("id"), int(request.body.get("point", 0)), request.actor)
        return Response.json(self.shown(self.repository.find(request.number("id"))))

    def short_check(self, request: Request) -> Response:
        self.actions.short_check(request.number("id"), int(request.body.get("point", 0)), str(request.body.get("shortfall", "")), request.actor)
        return Response.json(self.shown(self.repository.find(request.number("id"))))

    def merge(self, request: Request) -> Response:
        self.actions.merge(request.number("id"), request.actor)
        return Response.json(self.shown(self.repository.find(request.number("id"))))

    def release(self, request: Request) -> Response:
        return Response.json(self.shown(self.actions.release(request.number("id"), request.actor)))

    def send(self, request: Request) -> Response:
        return Response.json(self.shown(self.actions.send(request.number("id"), str(request.body.get("brief", "")), "", request.actor)))

    def message(self, request: Request) -> Response:
        return Response.json(self.shown(self.actions.user_message(request.number("id"), str(request.body.get("text", "")), request.actor)))

    def stop(self, request: Request) -> Response:
        return Response.json(self.shown(self.actions.stop(request.number("id"), str(request.body.get("why", "")), request.actor)))

    def complete(self, request: Request) -> Response:
        return Response.json(self.shown(self.actions.complete(request.number("id"), str(request.body.get("why", "")), request.actor)[0]))

    def rows(self) -> list[Worker]:
        return self.repository.scoped()

    def is_open(self, row: Worker) -> bool:
        return row.is_active()

    def index_page(self, rows: list[Worker]) -> list[dict]:
        return [self.own_fields(w) for w in rows]

    def own_fields(self, worker: Worker) -> dict:
        return {**ModelFields.build(worker), "files": worker.files_line(), "conversation": worker.conversation()}

    def shown_page(self, rows: list[Worker]) -> list[dict]:
        holdings, reports = self.tasks.worker_holdings(), self.reports.lasts(rows)
        views = self.task_views(rows, holdings)
        agent_ids = self.agents.session_numbers({w.session for w in rows})
        former_tasks, queues = self.tasks.earlier_tasks(rows, holdings), self.tasks.queues(rows)
        return [{**self.own_fields(w), "task": views.get(w.row_id, WorkerTaskView()), "earlier_task": former_tasks.get(w.row_id), "queue": [{"id": task.id, "title": task.title} for task in queues.get(w.row_id, [])],
                 "agent": agent_ids.get(w.session, 0), "report": reports[w.row_id]} for w in rows]

    def task_views(self, rows: list[Worker], holdings: dict[int, int]) -> dict[int, WorkerTaskView]:
        numbers = {w.row_id for w in rows}
        worker_tasks = {worker: task for task, worker in holdings.items() if worker in numbers}
        tasks = {task.row_id: task for task in self.tasks.numbered(worker_tasks.values())}
        todos, proofs = self.todos.task_lists(set(tasks)), self.proofs.grouped(set(tasks))
        return {worker: WorkerTaskView.built(tasks[task], todos.get(task, []), proofs.get(task, [])) for worker, task in worker_tasks.items() if task in tasks}
