from journal.chat.moment_cards import MomentCards
from journal.events.listener import Listener
from journal.events.moments.menu_answered import MenuAnswered
from journal.support.card_type import CardType


class MenuAnswerCard(Listener[MenuAnswered]):
    """A menu the journal answered in an agent's terminal is one mark in the chat saying which menu and what was done."""

    def __init__(self, cards: MomentCards) -> None:
        self.cards = cards

    def handle(self, event: MenuAnswered) -> None:
        self.cards.show(event.environment_id, event.session, "The journal answered a question the agent's tool asked", f"The journal {event.menu_choice}.", shows=CardType.MENUS)
