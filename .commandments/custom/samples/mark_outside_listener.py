class ImpasseCommand:
    def __init__(self, cards) -> None:
        self.cards = cards

    def stuck(self, why: str) -> None:
        # @sin MarkWrittenOutsideListenerDetector
        self.cards.show(1, "s1", "Agent stuck", "warn", "bad", why)

    def moved(self, why: str) -> None:
        # @sin MarkWrittenOutsideListenerDetector
        self.cards.show_fields(1, "s1", "Moved", {}, why)

    def other(self, rows) -> None:
        # @righteous MarkWrittenOutsideListenerDetector
        rows.show(1)


    def comment(self, messages, name: str) -> None:
        # @sin SystemMessageOutsideListenerDetector
        messages.save(Message(author=Author.SYSTEM, text=f"{name} commented"), None)
        # @righteous SystemMessageOutsideListenerDetector
        messages.save(Message(author=Author.USER, text=name), None)
