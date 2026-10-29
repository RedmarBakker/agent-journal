from journal.chat.moment_cards import MomentCards
from journal.events.listener import Listener
from journal.events.moments.search_completed import SearchCompleted
from journal.support.actor import Actor
from journal.support.card_type import CardType


class SearchCard(Listener[SearchCompleted]):
    """A search is one mark in the chat naming the words and how many results it found, each result a child of the mark that opens its row."""

    def __init__(self, cards: MomentCards) -> None:
        self.cards = cards

    def handle(self, event: SearchCompleted) -> None:
        label = f"Searched for \"{event.terms}\", {self.result_count(len(event.hits))}"
        data = {"kind": "search", "row": "", "terms": event.terms, "results": [hit.card_result() for hit in event.hits]}
        self.cards.show_fields(event.environment_id, event.session, label, data, Actor.system(), CardType.SEARCHES)

    @staticmethod
    def result_count(count: int) -> str:
        if not count:
            return "no results"
        return "1 result" if count == 1 else f"{count} results"
