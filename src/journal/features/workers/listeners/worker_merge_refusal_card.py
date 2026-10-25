from journal.chat.card_detail import CardDetail
from journal.chat.moment_cards import MomentCards
from journal.events.listener import Listener
from journal.events.moments.worker_merge_refused import WorkerMergeRefused
from journal.models.support.ref import Ref
from journal.support.actor import Actor
from journal.support.card_kind import CardKind


class WorkerMergeRefusalCard(Listener[WorkerMergeRefused]):
    """A merge refused on a clash is one mark in the chat of the agent that sent the worker, its detail where it clashes and the line that says so with the command that sends the worker back."""

    def __init__(self, cards: MomentCards) -> None:
        self.cards = cards

    def handle(self, event: WorkerMergeRefused) -> None:
        data = {"kind": "card", "icon": "agents", "tone": "bad", "row": str(Ref("workers", event.worker)), "command": "", "task": event.task}
        actor = Actor.agent(event.dispatcher) if event.dispatcher else Actor.system()
        label = CardDetail.shortened(f"Worker {event.worker}, {event.name}: merge of task {event.task} refused, its branch clashes with this one")
        self.cards.show_fields(event.environment_id, event.dispatcher, label, data, actor, CardKind.WORKERS, detail=f"{event.clashing}\n{event.line}")
