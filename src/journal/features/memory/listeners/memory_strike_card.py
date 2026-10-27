from journal.events.listener import Listener
from journal.events.models.deleted import Deleted
from journal.features.memory.listeners.memory_card import MemoryCard


class MemoryStrikeCard(MemoryCard, Listener[Deleted]):
    """A rule or a reminder struck is a card in the chat, so the user sees what no longer holds."""

    def handle(self, event: Deleted) -> None:
        self.show(event.model, event.actor, "struck")
