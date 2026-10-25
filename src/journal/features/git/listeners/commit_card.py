from journal.chat.moment_cards import MomentCards
from journal.events.listener import Listener
from journal.events.moments.git_committed import GitCommitted
from journal.support.actor import Actor
from journal.support.card_kind import CardKind

COMMIT = "commit"


class CommitCard(Listener[GitCommitted]):
    """A commit made in an agent's session is one mark in its chat, whatever ran it, alone or chained, and once for each commit."""

    def __init__(self, cards: MomentCards) -> None:
        self.cards = cards

    def handle(self, event: GitCommitted) -> None:
        actor = Actor.agent(event.session) if event.session else Actor.system()
        key = f"{COMMIT}:{event.sha}"
        if self.cards.is_shown(key, actor):
            return
        files = f"{event.files} file" + ("" if event.files == 1 else "s")
        self.cards.show(event.environment_id, event.session, f"Committed {files} on {event.branch}: {event.subject}", actor=actor, key=key, shows=CardKind.COMMITS)
