from journal.support.card_outcome import CardOutcome
from journal.chat.moment_cards import MomentCards
from journal.events.moments.fault_moment import FaultMoment
from journal.events.listener import Listener
from journal.events.moments.guard_failed import GuardFailed
from journal.events.moments.session_unbound import SessionUnbound
from journal.support.card_type import CardType


class FaultCards(Listener[FaultMoment]):
    """A session that started unbound and a guard that failed are each one mark in the chat, in red."""

    def __init__(self, cards: MomentCards) -> None:
        self.cards = cards

    def handle(self, event: FaultMoment) -> None:
        if isinstance(event, SessionUnbound):
            self.cards.show(event.environment_id, event.session, "An agent session started that the journal could not match to this project, so it is not followed", shows=CardType.FAULTS, outcome=CardOutcome.WARNED)
        if isinstance(event, GuardFailed):
            self.cards.show(event.environment_id, event.session, "A safety check failed, so the agent was not stopped", detail=event.text, shows=CardType.FAULTS, outcome=CardOutcome.WARNED)
