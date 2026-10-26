from journal.chat.card_detail import CardDetail
from journal.chat.moment_cards import MomentCards
from journal.events.listener import Listener
from journal.events.moments.worker_work_merged import WorkerWorkMerged
from journal.models.support.ref import Ref
from journal.support.actor import Actor
from journal.support.card_type import CardType


class WorkerStartedCard(Listener[WorkerWorkMerged]):
    """A merge that sends the worker on to the next task of its queue is a second mark in the chat, naming that task; with no next task it writes none."""

    def __init__(self, cards: MomentCards) -> None:
        self.cards = cards

    def handle(self, event: WorkerWorkMerged) -> None:
        if not event.next_task:
            return
        label = CardDetail.shortened(f"Worker {event.worker}, {event.name}: started on task {event.next_task}")
        data = {"kind": "card", "row": str(Ref("workers", event.worker)), "command": "", "task": event.next_task}
        actor = Actor.agent(event.dispatcher) if event.dispatcher else Actor.system()
        self.cards.show_fields(event.environment_id, event.dispatcher, label, data, actor, CardType.WORKERS)
