from journal.events.listener import Listener
from journal.events.moments.reader_added import ReaderAdded
from journal.features.shell.support.readers import Readers
from journal.repositories.reader_suggestions import ReaderSuggestions
from journal.support.actor import Actor


class ReaderSuggestionClear(Listener[ReaderAdded]):
    """A reader added takes away the suggestions of the parts it reads, so a part left with no reader again is suggested afresh."""

    def __init__(self, suggestions: ReaderSuggestions, readers: Readers) -> None:
        self.suggestions, self.readers = suggestions, readers

    def handle(self, event: ReaderAdded) -> None:
        self.suggestions.cleared(self.readers.reading_parts(list(self.suggestions.suggestion_times())), Actor.system())
