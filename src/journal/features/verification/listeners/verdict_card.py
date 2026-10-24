from journal.chat.moment_cards import MomentCards
from journal.events.listener import Listener
from journal.events.rows.reader_report_judged import ReaderReportJudged
from journal.features.workers.support.worker_process_card import WorkerProcessCard
from journal.models.support.ref import Ref
from journal.repositories.workers import Workers
from journal.support.actor import Actor
from journal.support.card_kind import CardKind


class VerdictCard(Listener[ReaderReportJudged]):
    """A verifier's verdict is a mark in the chat: the dismissal sound or refuted, with the verifier's reason."""

    def __init__(self, workers: Workers, cards: MomentCards) -> None:
        self.workers, self.cards = workers, cards

    def handle(self, event: ReaderReportJudged) -> None:
        for verifier in self.workers.session_worker(event.verifier_session):
            verdict = "the dismissal is sound" if event.is_sound else "the dismissal is refuted"
            self.cards.show(verifier.environment_id, None, WorkerProcessCard.label(verifier, verdict), WorkerProcessCard.icon(verifier), tone="good" if event.is_sound else "bad", detail=event.reason, row=Ref.build(verifier), actor=Actor.system(), key=f"verdict:{verifier.id}", shows=CardKind.WORKERS)
