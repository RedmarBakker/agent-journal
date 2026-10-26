from journal.support.card_outcome import CardOutcome
from journal.events.agent.line_delivered import LineDelivered
from journal.events.agent_listener import AgentListener
from journal.support.card_type import CardType
from journal.chat.moment_cards import MomentCards
from journal.features.workers.workers_nudges import WorkersNudges


class DispatchRefusalCards(AgentListener[LineDelivered]):
    """A dispatch blocked in favour of idle workers is one mark in the chat: refused, and how many idle workers could take it, with the idle list in its lines."""

    def __init__(self, cards: MomentCards) -> None:
        self.cards = cards

    def handle(self, event: LineDelivered) -> None:
        if event.nudge not in (WorkersNudges.WORKER_KNOWS_FILES.key, WorkersNudges.IDLE_CAP.key):
            return
        count = int(event.values["count"])
        self.cards.show(event.environment_id, event.session, f"Dispatch refused, {count} idle {'worker' if count == 1 else 'workers'} could take it", detail=f"idle workers:\n{event.values['workers']}", shows=CardType.WORKERS, outcome=CardOutcome.WARNED)
