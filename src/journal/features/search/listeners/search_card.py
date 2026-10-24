from journal.chat.moment_cards import MomentCards
from journal.events.listener import Listener
from journal.events.moments.search_made import SearchMade
from journal.support.card_kind import CardKind


class SearchCard(Listener[SearchMade]):
    """A search is one mark in the chat that opens what was found."""

    def __init__(self, cards: MomentCards) -> None:
        self.cards = cards

    def handle(self, event: SearchMade) -> None:
        self.cards.show(event.environment_id, event.session, f"Searched for \"{event.terms}\"", "search", detail=event.answer, kind="search", shows=CardKind.SEARCHES)
