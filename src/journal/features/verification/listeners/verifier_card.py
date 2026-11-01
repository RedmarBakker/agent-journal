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
from journal.models.support.ref import Ref
from journal.chat.process_card_contents import ProcessCardContents


class VerifierCard(Listener[ModelEvent]):
    """A verifier's card follows its linked report and its verdict, or its end without one."""

    def __init__(self, links: Links, reports: ReaderReports, card: VerifierProcessCard, cards: ProcessCards) -> None:
        self.links, self.reports, self.card, self.cards = links, reports, card, cards

    def handle(self, event: ModelEvent) -> None:
        if not isinstance(event, (Created, Updated)) or not isinstance(event.model, Verifier):
            return
        targets = self.links.targets(event.model, VERIFIES)
        if targets:
            self.cards.show(self.contents(event.model, targets[-1]))

    def contents(self, verifier: Verifier, judged: Ref) -> ProcessCardContents:
        return self.card.card_contents(verifier, self.reports.find(judged.id))
