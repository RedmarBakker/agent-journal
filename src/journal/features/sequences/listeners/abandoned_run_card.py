from journal.chat.moment_cards import MomentCards
from journal.events.listener import Listener
from journal.events.moments.sequence_abandoned import SequenceAbandoned
from journal.models.support.ref import Ref
from journal.support.card_kind import CardKind


class AbandonedRunCard(Listener[SequenceAbandoned]):
    """A run given up is one mark in the chat with why and the steps left undone."""

    def __init__(self, cards: MomentCards) -> None:
        self.cards = cards

    def handle(self, event: SequenceAbandoned) -> None:
        self.cards.show(event.environment_id, event.session, f"Sequence {event.sequence_id}, {event.title}, abandoned at step {event.step + 1}: {event.explanation}", "bolt", "bad", f"left undone: {event.skipped}", Ref("sequences", event.sequence_id), shows=CardKind.SEQUENCES)
