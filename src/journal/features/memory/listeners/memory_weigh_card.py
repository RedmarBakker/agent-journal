from journal.chat.moment_cards import MomentCards
from journal.events.listener import Listener
from journal.events.rows.memory_weighed import MemoryWeighed
from journal.models.support.ref import Ref
from journal.support.card_type import CardType

MEMORIES = "memories"


class MemoryWeighCard(Listener[MemoryWeighed]):
    """A memory given a new weight is a card in the chat, opening the memory."""

    def __init__(self, cards: MomentCards) -> None:
        self.cards = cards

    def handle(self, event: MemoryWeighed) -> None:
        self.cards.show(event.environment_id, event.session, f"Memory {event.row_id}: importance set to {event.weight} of 10", "", Ref(MEMORIES, event.row_id), shows=CardType.MEMORIES)
