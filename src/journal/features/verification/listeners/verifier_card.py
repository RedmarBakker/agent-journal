from journal.chat.process_cards import ProcessCards
from journal.events.listener import Listener
from journal.events.models.model_event import ModelEvent
from journal.events.models.created import Created
from journal.events.models.updated import Updated
from journal.features.verification.support.verifier_dispatch import VERIFIES
from journal.features.verification.support.verifier_process_card import VerifierProcessCard
from journal.models.verifier import Verifier
from journal.repositories.links import Links
from journal.repositories.reader_reports import ReaderReports
from journal.repositories.workers import Workers
from journal.models.support.ref import Ref
from journal.models.worker import Worker
from journal.chat.process_card_contents import ProcessCardContents


class VerifierCard(Listener[ModelEvent]):
    """A verifier's card follows its row: shown once it judges a report or a merged worker's model, the row it was linked to last, and turned to its verdict, or to its end without one."""

    def __init__(self, links: Links, reports: ReaderReports, workers: Workers, card: VerifierProcessCard, cards: ProcessCards) -> None:
        self.links, self.reports, self.workers, self.card, self.cards = links, reports, workers, card, cards

    def handle(self, event: ModelEvent) -> None:
        if not isinstance(event, (Created, Updated)) or not isinstance(event.model, Verifier):
            return
        targets = self.links.targets(event.model, VERIFIES)
        if targets:
            self.cards.show(self.contents(event.model, targets[-1]))

    def contents(self, verifier: Verifier, judged: Ref) -> ProcessCardContents:
        if judged.type == Worker.table():
            return self.card.fit_card_contents(verifier, self.workers.find(judged.id))
        return self.card.card_contents(verifier, self.reports.find(judged.id))
