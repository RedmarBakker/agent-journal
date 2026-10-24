from journal.chat.process_cards import ProcessCards
from journal.events.listener import Listener
from journal.events.models.saved import Saved
from journal.features.suggestions.support.suggestion_process_card import SuggestionProcessCard
from journal.features.suggestions.support.suggestion_search import SuggestionSearch
from journal.models.suggestion import Suggestion
from journal.repositories.scope import Scope


class SuggestionCard(Listener[Saved]):
    """A suggestion made is a process card in the chat, in the environment of the agent present, and answering it settles that card in place."""

    def __init__(self, card: SuggestionProcessCard, cards: ProcessCards, search: SuggestionSearch, scope: Scope) -> None:
        self.card, self.cards, self.search, self.scope = card, cards, search, scope

    def handle(self, event: Saved) -> None:
        suggestion = event.model
        if not isinstance(suggestion, Suggestion):
            return
        environment_id = self.search.card_environment(suggestion)
        with self.scope.environment(environment_id):
            self.cards.show(self.card.mark(suggestion, self.search.lookup(suggestion.key), environment_id))
