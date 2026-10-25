from journal.repositories.tasks import Tasks
from datetime import datetime, timezone

from journal.features.reviewing.support.review_routing import ReviewRouting
from journal.support.actor import Actor
from journal.models.author import Author
from journal.models.link import Link
from journal.models.message import Message
from journal.models.support.ref import Ref
from journal.models.worker import Worker
from journal.models.worker_state import WorkerState
from journal.repositories.links import Links
from journal.repositories.messages import Messages
from journal.repositories.workers import Workers


REPORTED = "reported"


class WorkerReports:
    """A worker's report, filed the one way: as a message in the chat in the worker's name, linked from the worker, and the worker marked reported, or, for a clock-out, marked clocked out and its work sent to the journal's reviewer when the review routing is on, a pool worker's aside, whose work is on another machine."""

    def __init__(self, workers: Workers, messages: Messages, links: Links, routing: ReviewRouting, tasks: Tasks) -> None:
        self.workers, self.messages, self.links, self.routing, self.tasks = workers, messages, links, routing, tasks

    def file(self, worker: Worker, text: str, actor: Actor) -> Message:
        message = self.posted(worker, text, actor)
        self.workers.save(worker.reported(datetime.now(timezone.utc).timestamp(), message.row_id), actor)
        return message

    def delivered(self, worker: Worker, text: str, actor: Actor) -> None:
        self.posted(worker, text, actor)
        current, time = self.workers.find(worker.row_id), datetime.now(timezone.utc).timestamp()
        self.workers.save(current.review_requested(time, text) if self.routing.is_enabled() and not worker.pool_request else current.delivered(time), actor)

    # the task a worker moved on to inside its queue and has not clocked out of, or 0 when it made no move
    def moved_task(self, worker: Worker) -> int:
        holder = Ref.build(worker)
        return next(iter(self.tasks.holder_task_ids(holder)), 0) if self.tasks.finished_task_ids(holder) else 0

    # where every task of a worker's queue stands when its run ends without a clock-out: finished and waiting, cut short, still queued
    def queue_line(self, worker: Worker) -> str:
        holder = Ref.build(worker)
        parts = (("finished, waiting for the merge", self.tasks.finished_task_ids(holder)), ("cut short", self.tasks.holder_task_ids(holder)), ("still queued", tuple(task.id for task in self.tasks.queue(holder))))
        standings = [f"{label}: {', '.join(f'task {task_id}' for task_id in task_ids)}" for label, task_ids in parts if task_ids]
        return "; ".join(standings) if self.tasks.finished_task_ids(holder) or self.tasks.queue(holder) else ""

    def posted(self, worker: Worker, text: str, actor: Actor) -> Message:
        message = self.messages.save(Message(environment_id=worker.environment_id, author=Author.AGENT, text=f"{self.lead(worker)}{text}", data={"kind": Message.REPORT, "worker": worker.name, "worker_id": worker.id, "task": next(iter(self.tasks.holder_task_ids(Ref.build(worker))), 0)}), actor)
        self.links.save(Link(source=Ref.build(worker), target=Ref.build(message), kind=REPORTED), actor)
        return message

    # the last report of each of the workers, read with one query for their links and one for the messages
    def lasts(self, workers: list[Worker]) -> dict[int, str]:
        latest = {link.source.id: link.target.id for link in self.links.model_links("source", workers, REPORTED)}
        texts = {message.row_id: message.text for message in self.messages.numbered(latest.values())}
        return {worker.row_id: texts.get(latest.get(worker.row_id, 0), "").removeprefix(self.lead(worker)) if worker.state != WorkerState.DISPATCHED else "" for worker in workers}

    def last(self, worker: Worker) -> str:
        reports = self.links.targets(worker, REPORTED)
        if worker.state == WorkerState.DISPATCHED or not reports:
            return ""
        return self.messages.find(reports[-1].id).text.removeprefix(self.lead(worker))

    @staticmethod
    def lead(worker: Worker) -> str:
        return f"{worker.name} reports: "
