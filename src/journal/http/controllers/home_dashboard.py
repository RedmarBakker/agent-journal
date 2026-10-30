from journal.features.workers.support.merged_work import MergedWork
from journal.http.controllers.tasks import TaskController
from journal.http.support.request import Request
from journal.models.check import Check
from journal.models.message import Message
from journal.models.question import Question
from journal.models.task import Task
from journal.models.task_state import TaskState
from journal.models.worker import JOB_STARTS, MERGED, Worker
from journal.models.support.ref import Ref
from journal.repositories.messages import Messages
from journal.repositories.plans import PLAN_LINK
from journal.repositories.tasks import Tasks
from journal.repositories.workers import Workers
from journal.support.card_type import CardType
from journal.support.response import Response

MERGE_CARDS = 2000
LATEST_MERGES = 4


class HomeDashboardController:
    """The blocked tasks and latest worker merges shown on Home."""

    def __init__(self, task_controller: TaskController, tasks: Tasks, workers: Workers, messages: Messages, merged_work: MergedWork) -> None:
        self.task_controller, self.tasks, self.workers = task_controller, tasks, workers
        self.messages, self.merged_work = messages, merged_work

    def index(self, request: Request) -> Response:
        return Response.json({"blocked_tasks": self.blocked_tasks(), "latest_merges": self.latest_merges()})

    def blocked_tasks(self) -> list[dict]:
        tasks = self.tasks.selected(self.tasks.query().filter(state=TaskState.BLOCKED).order_descending("updated_at").order_descending("id"))
        rows = self.task_controller.shown_page(tasks)
        return [{**row, "wait_reasons": self.wait_reasons(task)} for task, row in zip(tasks, rows)]

    def wait_reasons(self, task: Task) -> list[str]:
        reasons = [task.block_reason] if task.block_reason else []
        reasons.extend(self.wait_reason(ref) for ref in self.tasks.open_waits(task))
        return reasons or ["No wait is recorded."]

    def wait_reason(self, ref: Ref) -> str:
        waiting = self.tasks.waiting(ref)
        if isinstance(waiting, Task):
            reason = f'task {waiting.id}, "{waiting.title}"'
            worker_id = self.tasks.task_worker_holdings({waiting.id}).get(waiting.id)
            worker = self.worker(worker_id) if worker_id else None
            return f"{reason}, which {worker.name} is still on" if worker else reason
        if isinstance(waiting, Question):
            return f'your answer to "{waiting.text}"'
        if isinstance(waiting, Check):
            return f'check {waiting.id}, "{waiting.title}"'
        return f"{ref.type[:-1]} {ref.id}"

    def latest_merges(self) -> list[dict]:
        history = self.merge_cards()
        latest = history[:LATEST_MERGES]
        worker_ids = {self.worker_id(card) for card in latest}
        worker_history = [card for card in history if self.worker_id(card) in worker_ids]
        workers = self.workers_for(worker_history)
        tasks = self.tasks_for(latest)
        plan_refs = self.tasks.linked(PLAN_LINK, {card.data["task"] for card in latest})
        spans = self.merge_spans(worker_history, workers)
        return [self.merge(card, workers, tasks, plan_refs, spans) for card in latest]

    def merge_cards(self) -> list[Message]:
        cards = self.messages.newest_moments((CardType.WORKERS,), MERGE_CARDS)
        return [card for card in cards if self.is_merge(card) and self.worker_id(card)]

    @staticmethod
    def is_merge(card: Message) -> bool:
        task = card.data.get("task")
        return type(task) is int and card.text.endswith(f"work on task {task} merged")

    def workers_for(self, cards: list[Message]) -> dict[int, Worker]:
        ids = {self.worker_id(card) for card in cards}
        rows = self.workers.selected(self.workers.query().filter_listed("id", ids)) if ids else []
        return {worker.id: worker for worker in rows}

    def tasks_for(self, cards: list[Message]) -> dict[int, Task]:
        tasks = self.tasks.tasks_numbered({int(card.data["task"]) for card in cards})
        return {task.id: task for task in tasks}

    def merge_spans(self, cards: list[Message], workers: dict[int, Worker]) -> dict[int, tuple[float, float]]:
        grouped: dict[int, list[Message]] = {}
        for card in cards:
            grouped.setdefault(self.worker_id(card), []).append(card)
        spans = {}
        for worker_id, events in grouped.items():
            worker = workers.get(worker_id)
            if worker is None:
                continue
            steps = [(index, at) for index, (word, at) in enumerate(worker.moves.steps) if word == MERGED]
            for card, (index, end) in zip(sorted(events, key=lambda item: item.id), steps[-len(events):]):
                start = next((at for word, at in reversed(worker.moves.steps[:index]) if word in JOB_STARTS), end)
                spans[card.id] = (start, end)
        return spans

    def merge(self, card: Message, workers: dict[int, Worker], tasks: dict[int, Task], plan_refs: dict[int, list[Ref]], spans: dict[int, tuple[float, float]]) -> dict:
        worker = workers.get(self.worker_id(card))
        task_id = int(card.data["task"])
        task = tasks.get(task_id)
        span = spans.get(card.id)
        start, end = span if span else (0.0, card.created_at.timestamp())
        edits = self.merged_work.job_edits_between(worker, start, end) if worker and span else []
        linked = plan_refs.get(task_id, [])
        return {"task_id": task_id, "task_title": task.title if task else f"Task {task_id}",
                "plan_id": linked[0].id if linked else (worker.plan_id if worker else 0),
                "branch": worker.branch if worker else "", "worker": (worker.role or worker.name) if worker else "",
                "merged_at": self.merged_at(card, end), "added": sum(edit.added for edit in edits), "removed": sum(edit.removed for edit in edits)}

    def merged_at(self, card: Message, end: float) -> str:
        return self.merged_work.moment(end).isoformat() if end else card.created_at.isoformat()

    def worker(self, worker_id: int) -> Worker | None:
        rows = self.workers.numbered(worker_id)
        return rows[0] if rows else None

    @staticmethod
    def worker_id(card: Message) -> int:
        row = str(card.data.get("row", ""))
        kind, separator, number = row.partition(":")
        return int(number) if separator and kind == Worker.table() and number.isdigit() else 0
