from journal.support.card_outcome import CardOutcome
from journal.chat.card_detail import CardDetail
from journal.chat.moment_cards import MomentCards
from journal.events.listener import Listener
from journal.events.moments.worker_work_merged import WorkerWorkMerged
from journal.models.support.ref import Ref
from journal.support.actor import Actor
from journal.support.card_kind import CardKind


class WorkerMergeCard(Listener[WorkerWorkMerged]):
    """A merge is one mark in the chat, naming the task merged and the task the worker went on to, or that it is idle; the task's own finish, the worker's merged standing and its next job write none."""

    def __init__(self, cards: MomentCards) -> None:
        self.cards = cards

    def handle(self, event: WorkerWorkMerged) -> None:
        then = f"it went on to task {event.next_task}" if event.next_task else "it is idle"
        label = CardDetail.shortened(f"Worker {event.worker}, {event.name}: work on task {event.task} merged; {then}")
        row = Ref("workers", event.worker)
        data = {"kind": "card", "outcome": str(CardOutcome.PASSED), "row": str(row), "command": "", "task": event.task}
        actor = Actor.agent(event.dispatcher) if event.dispatcher else Actor.system()
        self.cards.show_fields(event.environment_id, event.dispatcher, label, data, actor, CardKind.WORKERS)
