from journal.events.listener import Listener
from journal.events.models.created import Created
from journal.features.memory.listeners.memory_card import MemoryCard


class MemoryRowCard(MemoryCard, Listener[Created]):
    """A fact, a rule or a reminder recorded is a card in the chat, as version 3 showed it: its number with a check mark, and the row it opens."""

    def handle(self, event: Created) -> None:
        self.show(event.model, event.actor, "recorded", "check", "")
