from journal.support.card_outcome import CardOutcome
from journal.chat.moment_cards import MomentCards
from journal.events.listener import Listener
from journal.events.moments.sequence_abandoned import SequenceAbandoned
from journal.models.support.ref import Ref
from journal.support.card_type import CardType


class AbandonedRunCard(Listener[SequenceAbandoned]):
    """A run given up is one mark in the chat with why and the steps left undone."""

    def __init__(self, cards: MomentCards) -> None:
        self.cards = cards

    def handle(self, event: SequenceAbandoned) -> None:
        self.cards.show(event.environment_id, event.session, f"{event.title} was stopped at step {event.step + 1}: {event.explanation}", f"Steps not done: {event.skipped}", Ref("sequences", event.sequence_id), shows=CardType.SEQUENCES, outcome=CardOutcome.WARNED)
