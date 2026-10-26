from journal.support.card_outcome import CardOutcome
import time

from journal.support.masks import Masks
from journal.chat.moment_cards import MomentCards
from journal.events.agent.ticked import Ticked
from journal.events.agent_listener import AgentListener
from journal.support.card_type import CardType
from journal.support.time_source import TimeSource

ALARM_INTERVAL_SECONDS = 600.0


class LeakAlarm(AgentListener[Ticked]):
    """A secret's value that reached a write was masked there; at the next tick the user is shown which, so the leak is seen and not only stopped."""

    def __init__(self, masks: Masks, cards: MomentCards, time_source: TimeSource) -> None:
        self.time_source = time_source
        self.masks, self.cards = masks, cards
        self._said_at = 0.0

    def handle(self, event: Ticked) -> None:
        if not self.masks.leaks or self.time_source.seconds() - self._said_at < ALARM_INTERVAL_SECONDS:
            return
        variables = sorted({variable for variable, _ in self.masks.leaks})
        self.masks.leaks.clear()
        self._said_at = self.time_source.seconds()
        self.cards.show(event.environment_id, event.session, f"A secret's value was about to be recorded and was masked: {', '.join(variables)}", shows=CardType.FAULTS, outcome=CardOutcome.WARNED)
