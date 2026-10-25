from journal.chat.moment_cards import MomentCards
from journal.chat.process_cards import ProcessCards
from journal.events.listener import Listener
from journal.events.models.created import Created
from journal.events.models.model_event import ModelEvent
from journal.events.models.updated import Updated
from journal.features.workers.support.worker_process_card import FAILED, WorkerProcessCard
from journal.models.support.ref import Ref
from journal.models.worker import Worker
from journal.models.worker_state import WorkerState
from journal.support.actor import Actor
from journal.support.card_kind import CardKind


class WorkerCards(Listener[ModelEvent]):
    """A worker's dispatch is one process card in the chat, which changes only when the dispatch itself failed, red with why; every later standing it reaches, finished and ready to check, stopped before it finished, reported, stopped or released, is a moment card at the bottom of the chat, one per move, and its clock-in none, since its dispatch or its next job already says it started; its merge is WorkerMergeCard's one mark, and its other moments are marks of their own, WorkerMomentCards."""

    def __init__(self, card: WorkerProcessCard, cards: MomentCards, processes: ProcessCards) -> None:
        self.card, self.cards, self.processes = card, cards, processes

    def handle(self, event: ModelEvent) -> None:
        if not isinstance(event, (Created, Updated)) or not isinstance(event.model, Worker):
            return
        worker = event.model
        standing = self.card.standing(worker)
        if worker.state in (WorkerState.READY, WorkerState.MERGED) or (worker.state == WorkerState.DISPATCHED and worker.reuse_count):
            return
        actor = Actor.agent(worker.dispatcher) if worker.dispatcher else Actor.system()
        if worker.state == WorkerState.DISPATCHED or standing.text == FAILED:
            contents = self.card.card_contents(worker, standing, actor)
            if contents:
                self.processes.show(contents)
            return
        key = f"worker:{worker.id}:{worker.state}:{worker.silence.timeout.start}"
        if not self.cards.is_shown(key, actor):
            self.cards.show(worker.environment_id, worker.dispatcher, self.card.label(worker, standing.text), self.card.icon(worker), tone=standing.tone, detail=standing.detail, row=Ref.build(worker), actor=actor, key=key, shows=CardKind.WORKERS)
