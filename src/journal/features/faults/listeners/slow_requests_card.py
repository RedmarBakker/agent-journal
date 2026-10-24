from journal.chat.process_cards import ProcessCards
from journal.events.listener import Listener
from journal.events.moments.slow_requests_reported import SlowRequestsReported
from journal.features.faults.support.slow_request_process_card import SlowRequestProcessCard


class SlowRequestsCard(Listener[SlowRequestsReported]):
    """The slow requests the agent is told of are one new process card in the chat."""

    def __init__(self, card: SlowRequestProcessCard, cards: ProcessCards) -> None:
        self.card, self.cards = card, cards

    def handle(self, event: SlowRequestsReported) -> None:
        self.cards.show(self.card.card_contents(event))
