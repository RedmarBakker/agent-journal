from journal.features.feature import Feature
from journal.features.search.commands.search_command import SearchCommand
from journal.features.search.listeners.search_card import SearchCard


class SearchFeature(Feature):
    name = "search"
    title = "Search"
    help = "journal search \"<words>\" finds every row and agent conversation here that holds all the words, and leaves a mark in the chat that opens what was found."
    commands = (SearchCommand,)
    listeners = (SearchCard,)
