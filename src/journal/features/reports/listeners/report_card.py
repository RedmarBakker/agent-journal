from journal.chat.process_cards import ProcessCards
from journal.chat.row_process_card import RowProcessCard
from journal.events.listener import Listener
from journal.events.models.created import Created
from journal.models.report import Report
from journal.support.actor_kind import ActorKind


class ReportCard(Listener[Created]):
    """A report an agent writes is a card in its environment's chat; DockNewWriting docks it above the chat."""

    def __init__(self, card: RowProcessCard, cards: ProcessCards) -> None:
        self.card, self.cards = card, cards

    def handle(self, event: Created) -> None:
        report = event.model
        if isinstance(report, Report) and event.actor.kind == ActorKind.AGENT:
            self.cards.show(self.card.card_contents(report.environment_id, report, event.actor))
