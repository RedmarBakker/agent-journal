from journal.chat.moment_cards import MomentCards
from journal.events.listener import Listener
from journal.events.moments.menu_answered import MenuAnswered
from journal.support.card_kind import CardKind


class MenuAnswerCard(Listener[MenuAnswered]):
    """A menu the journal answered in an agent's terminal is one mark in the chat saying which menu and what was done."""

    def __init__(self, cards: MomentCards) -> None:
        self.cards = cards

    def handle(self, event: MenuAnswered) -> None:
        self.cards.show(event.environment_id, event.session, f'A menu in the agent\'s terminal was answered: "{event.question[-160:]}" The journal {event.menu_choice}.', shows=CardKind.MENUS)
