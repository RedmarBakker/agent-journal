from journal.features.feature import Feature
from journal.features.suggestions.listeners.hourly_suggestion import HourlySuggestion
from journal.features.suggestions.support.suggestion_process_card import SuggestionProcessCard
from journal.features.suggestions.suggestions_options import SuggestionsOptions


class SuggestionsFeature(Feature):
    name = "suggestions"
    title = "Suggestions"
    help = "Looks for things worth suggesting, first a while after the journal starts and then hourly, and shows each once as a card in the chat: answered or not, it is never suggested again."
    options = (SuggestionsOptions.FIRST_DELAY, SuggestionsOptions.INTERVAL)
    listeners = (HourlySuggestion,)
    process_cards = (SuggestionProcessCard,)
