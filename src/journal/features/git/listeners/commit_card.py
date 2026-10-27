from journal.chat.moment_cards import MomentCards
from journal.events.listener import Listener
from journal.events.moments.git_committed import GitCommitted
from journal.support.actor import Actor
from journal.support.card_type import CardType

COMMIT = "commit"


class CommitCard(Listener[GitCommitted]):
    """A commit made in an agent's session is one mark in its chat, its hash and its branch as a chip, nothing of its message, whatever ran it, alone or chained, and once for each commit in its environment, whichever session saw it."""

    def __init__(self, cards: MomentCards) -> None:
        self.cards = cards

    def handle(self, event: GitCommitted) -> None:
        actor = Actor.agent(event.session) if event.session else Actor.system()
        key = f"{COMMIT}:{event.sha}"
        if self.cards.is_key_shown(key):
            return
        self.cards.show(event.environment_id, event.session, f"Committed a change on {event.branch}", event.sha[:8], actor=actor, key=key, shows=CardType.COMMITS)
