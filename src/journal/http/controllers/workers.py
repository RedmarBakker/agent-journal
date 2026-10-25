from journal.models.worker_state import WorkerState
from journal.features.workers.support.merge_steps import MergeSteps
from journal.db.query import Query
from journal.features.workers.support.worker_actions import WorkerActions
from journal.features.workers.support.worker_reports import WorkerReports
from journal.http.counts import Counts
from journal.http.row_list import RowList
from journal.http.support.request import Request
from journal.support.response import Response
from journal.http.controllers.controller import Controller
from journal.http.support.model_fields import ModelFields
from journal.features.workers.support.worker_task_view import WorkerTaskView
from journal.models.support.report_choice import ReportChoice
from journal.models.worker import Worker
from journal.repositories.agents import Agents
from journal.repositories.proofs import Proofs
from journal.repositories.tasks import Tasks
from journal.repositories.worker_todos import WorkerTodos
from journal.repositories.workers import Workers

ACTIVE_WORKER_STATES = (WorkerState.DISPATCHED, WorkerState.READY, WorkerState.DELIVERED)


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
        self.actions.merge(request.number("id"), request.actor, MergeSteps.silent())
        return Response.json(self.shown(self.repository.find(request.number("id"))))

    def report_choice(self, request: Request) -> Response:
        return Response.json(self.shown(self.actions.set_report_choice(request.number("id"), ReportChoice.argument(str(request.body.get("choice", "each")).split()), request.actor)))

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

    def index(self, request: Request) -> Response:
        if "tasks" not in request.query:
            return super().index(request)
        numbers = {int(n) for n in str(request.query["tasks"]).split(",") if n.strip().isdigit()}
        rows = self.repository.numbered(sorted(self.tasks.task_workers(numbers)))
        return Response.json(RowList(rows=self.shown_page(rows), is_last_page=True, counts=Counts(all=len(rows), open=len([w for w in rows if w.is_active()]), unread=0)))

    def open_rows(self, query: Query) -> Query:
        return query.filter_listed("state", ACTIVE_WORKER_STATES)

    def closed_rows(self, query: Query) -> Query:
        return query.filter_unlisted("state", ACTIVE_WORKER_STATES)

    def index_page(self, rows: list[Worker]) -> list[dict]:
        return [self.worker_fields(w) for w in rows]

    def worker_fields(self, worker: Worker) -> dict:
        return {**ModelFields.build(worker), "files": worker.files_line(), "conversation": worker.conversation()}

    def shown_page(self, rows: list[Worker]) -> list[dict]:
        holdings, reports = self.tasks.worker_task_holdings(rows), self.reports.lasts(rows)
        views = self.task_views(rows, holdings)
        agent_ids = self.agents.session_numbers({w.session for w in rows})
        former_tasks, queues, finished = self.tasks.earlier_tasks(rows, holdings), self.tasks.queues(rows), self.tasks.finished_ids(rows)
        return [{**self.worker_fields(w), "task": views.get(w.row_id, WorkerTaskView()), "earlier_task": former_tasks.get(w.row_id), "queue": [{"id": task.id, "title": task.title} for task in queues.get(w.row_id, [])], "finished": finished.get(w.row_id, []),
                 "holds": self.all_task_ids(w.row_id, views, queues), "agent": agent_ids.get(w.session, 0), "report": reports[w.row_id]} for w in rows]

    @staticmethod
    def all_task_ids(row_id: int, views: dict[int, WorkerTaskView], queues: dict) -> list[int]:
        current = [views[row_id].task_id] if row_id in views else []
        return current + [task.id for task in queues.get(row_id, [])]

    def task_views(self, rows: list[Worker], holdings: dict[int, int]) -> dict[int, WorkerTaskView]:
        numbers = {w.row_id for w in rows}
        worker_tasks = {worker: task for task, worker in holdings.items() if worker in numbers}
        tasks = {task.row_id: task for task in self.tasks.numbered(worker_tasks.values())}
        todos, proofs = self.todos.task_lists(set(tasks)), self.proofs.grouped(set(tasks))
        return {worker: WorkerTaskView.built(tasks[task], todos.get(task, []), proofs.get(task, [])) for worker, task in worker_tasks.items() if task in tasks}
