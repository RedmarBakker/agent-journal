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

    def __init__(self, workers: Workers, messages: Messages, links: Links, routing: ReviewRouting) -> None:
        self.workers, self.messages, self.links, self.routing = workers, messages, links, routing

    def file(self, worker: Worker, text: str, actor: Actor) -> Message:
        message = self.posted(worker, text, actor)
        self.workers.save(worker.reported(datetime.now(timezone.utc).timestamp(), message.row_id), actor)
        return message

    def delivered(self, worker: Worker, text: str, actor: Actor) -> None:
        self.posted(worker, text, actor)
        current, time = self.workers.find(worker.row_id), datetime.now(timezone.utc).timestamp()
        self.workers.save(current.delivered_to_review(time, text) if self.routing.is_on() and not worker.pool_request else current.delivered(time), actor)

    def posted(self, worker: Worker, text: str, actor: Actor) -> Message:
        message = self.messages.save(Message(environment_id=worker.environment_id, author=Author.AGENT, text=f"{self.lead(worker)}{text}", data={"kind": Message.REPORT, "worker": worker.name, "worker_id": worker.id}), actor)
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
