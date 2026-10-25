from journal.support.card_outcome import CardOutcome
from journal.chat.moment_cards import MomentCards
from journal.events.moments.fault_moment import FaultMoment
from journal.events.listener import Listener
from journal.events.moments.guard_failed import GuardFailed
from journal.events.moments.session_unbound import SessionUnbound
from journal.support.card_kind import CardKind


class FaultCards(Listener[FaultMoment]):
    """A session that started unbound and a guard that failed are each one mark in the chat, in red."""

    def __init__(self, cards: MomentCards) -> None:
        self.cards = cards

    def handle(self, event: FaultMoment) -> None:
        if isinstance(event, SessionUnbound):
            self.cards.show(event.environment_id, event.session, f"Session {event.session} started without the launch id of {event.environment}: the journal records its hooks and does not take it as this environment's agent", shows=CardKind.FAULTS, outcome=CardOutcome.WARNED)
        if isinstance(event, GuardFailed):
            self.cards.show(event.environment_id, event.session, f"A guard failed and let the event through: {event.text}", shows=CardKind.FAULTS, outcome=CardOutcome.WARNED)
