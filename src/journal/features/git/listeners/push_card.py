from journal.chat.moment_cards import MomentCards
from journal.events.listener import Listener
from journal.events.moments.git_pushed import GitPushed
from journal.support.actor import Actor
from journal.support.card_type import CardType


class PushCard(Listener[GitPushed]):
    """A push made in an agent's session is one mark in its chat, whatever ran it."""

    def __init__(self, cards: MomentCards) -> None:
        self.cards = cards

    def handle(self, event: GitPushed) -> None:
        actor = Actor.agent(event.session) if event.session else Actor.system()
        self.cards.show(event.environment_id, event.session, f"Pushed {event.branch}", actor=actor, shows=CardType.PUSHES)
