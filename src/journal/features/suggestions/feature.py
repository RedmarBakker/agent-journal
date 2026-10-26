from journal.support.card_family import CardFamily
from journal.support.card_type_entry import CardTypeEntry
from journal.support.card_type_catalogue import JOURNAL
from journal.support.card_type import CardType
from journal.features.feature import Feature
from journal.features.suggestions.listeners.hourly_suggestion import HourlySuggestion
from journal.features.suggestions.listeners.suggestion_card import SuggestionCard
from journal.features.suggestions.support.suggestion_process_card import SuggestionProcessCard
from journal.features.suggestions.suggestions_options import SuggestionsOptions


class SuggestionsFeature(Feature):
    name = "suggestions"
    card_families = (CardFamily("suggestions", "Suggestions", "bulb", JOURNAL),)
    card_types = (CardTypeEntry(CardType.SUGGESTIONS, "Suggestions", "suggestions"),)
    title = "Suggestions"
    help = "Looks for things worth suggesting, first a while after the journal starts and then hourly, and shows each once as a card in the chat: answered or not, it is never suggested again."
    options = (SuggestionsOptions.FIRST_DELAY, SuggestionsOptions.INTERVAL)
    listeners = (HourlySuggestion, SuggestionCard)
    process_cards = (SuggestionProcessCard,)
