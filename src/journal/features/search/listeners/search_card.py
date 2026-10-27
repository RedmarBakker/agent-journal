from journal.chat.moment_cards import MomentCards
from journal.events.listener import Listener
from journal.events.moments.search_completed import SearchCompleted
from journal.support.card_type import CardType


class SearchCard(Listener[SearchCompleted]):
    """A search is one mark in the chat that opens what was found."""

    def __init__(self, cards: MomentCards) -> None:
        self.cards = cards

    def handle(self, event: SearchCompleted) -> None:
        self.cards.show(event.environment_id, event.session, f"Searched for \"{event.terms}\"", detail=event.answer, type_name="search", shows=CardType.SEARCHES)
