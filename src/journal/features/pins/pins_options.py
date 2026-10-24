from journal.support.option import Option


class PinsOptions:
    PIN_SUGGESTION_INTERVAL = Option("pins.suggest_every", "Suggest an unpinned link again after", "The agent's tool uses before a link it has not pinned is suggested again", 50, unit="tool uses")
