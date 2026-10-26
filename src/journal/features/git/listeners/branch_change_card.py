from journal.chat.moment_cards import MomentCards
from journal.events.listener import Listener
from journal.events.moments.branch_changed import BranchChanged
from journal.support.actor import Actor
from journal.support.card_type import CardType


class BranchChangeCard(Listener[BranchChanged]):
    """A switch to a branch made in an agent's session is one mark in its chat, whatever ran it."""

    def __init__(self, cards: MomentCards) -> None:
        self.cards = cards

    def handle(self, event: BranchChanged) -> None:
        actor = Actor.agent(event.session) if event.session else Actor.system()
        self.cards.show(event.environment_id, event.session, f"Switched to branch {event.branch}", actor=actor, shows=CardType.BRANCH_SWITCHES)
