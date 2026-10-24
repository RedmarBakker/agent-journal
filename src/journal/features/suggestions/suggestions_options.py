from journal.support.option import Option


class SuggestionsOptions:
    """The options of the suggestions feature."""

    FIRST_DELAY = Option("suggestions.first_after", "First suggestions after", "Minutes after the journal starts before it first looks for something to suggest, so nothing greets you the moment it starts", 15, unit="minutes")
    INTERVAL = Option("suggestions.every", "Look for suggestions every", "Minutes between two looks for something to suggest, such as a package the journal could run as its plugin", 60, unit="minutes")
