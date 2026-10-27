from journal.chat.moment_cards import MomentCards
from journal.events.listener import Listener
from journal.events.moments.reader_guessed import ReaderGuessed
from journal.support.card_type import CardType


class GuessedReaderCard(Listener[ReaderGuessed]):
    """A reader the journal saved on its own is one mark in the agent's chat, so the user sees it, not only the agent."""

    def __init__(self, cards: MomentCards) -> None:
        self.cards = cards

    def handle(self, event: ReaderGuessed) -> None:
        self.cards.show(event.environment_id, event.session, f"Reader {event.reader} saved for {event.command}", f"made from output {event.output}: {event.subject}", shows=CardType.COMMANDS)
