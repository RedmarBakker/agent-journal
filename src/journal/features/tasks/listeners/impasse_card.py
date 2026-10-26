from journal.support.card_outcome import CardOutcome
from journal.chat.moment_cards import MomentCards
from journal.events.agent.impasse_report import ImpasseReport
from journal.events.agent_listener import AgentListener
from journal.support.card_type import CardType


class ImpasseCard(AgentListener[ImpasseReport]):
    """An agent that says it is stuck is one mark in the chat with its reason."""

    def __init__(self, cards: MomentCards) -> None:
        self.cards = cards

    def handle(self, event: ImpasseReport) -> None:
        self.cards.show(event.environment_id, event.session, "Agent stuck", event.reason, shows=CardType.IMPASSE, outcome=CardOutcome.WARNED)
