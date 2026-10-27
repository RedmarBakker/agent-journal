from journal.chat.moment_cards import MomentCards
from journal.events.listener import Listener
from journal.events.rows.memory_removed import MemoryRemoved
from journal.models.support.ref import Ref
from journal.support.card_type import CardType

MEMORIES = "memories"


class MemoryRemovalCard(Listener[MemoryRemoved]):
    """A memory taken out as no longer true is a card in the chat, opening the memory."""

    def __init__(self, cards: MomentCards) -> None:
        self.cards = cards

    def handle(self, event: MemoryRemoved) -> None:
        self.cards.show(event.environment_id, event.session, f"Memory {event.row_id} removed", "", Ref(MEMORIES, event.row_id), shows=CardType.MEMORIES)
