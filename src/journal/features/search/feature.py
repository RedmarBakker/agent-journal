from journal.support.card_family import CardFamily
from journal.support.card_type_entry import CardTypeEntry
from journal.support.card_type_catalogue import AGENT
from journal.support.card_type import CardType
from journal.features.feature import Feature
from journal.features.search.commands.search_command import SearchCommand
from journal.features.search.listeners.search_card import SearchCard


class SearchFeature(Feature):
    name = "search"
    card_families = (CardFamily("searches", "Searches", "search", AGENT),)
    card_types = (CardTypeEntry(CardType.SEARCHES, "Searches the agent ran", "searches"),)
    title = "Search"
    help = "journal search \"<words>\" finds every row and agent conversation here that holds all the words, and leaves a mark in the chat that opens what was found."
    commands = (SearchCommand,)
    listeners = (SearchCard,)
