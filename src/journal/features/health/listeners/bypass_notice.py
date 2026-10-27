from journal.support.card_outcome import CardOutcome
from journal.chat.moment_cards import MomentCards
from journal.events.agent.agent_event import AgentEvent
from journal.events.listener import Listener
from journal.features.health.support.bypass import Bypass
from journal.features.health.support.bypass_log import BypassLog
from journal.support.card_type import CardType


class BypassNotice(Listener[AgentEvent]):
    """The hooks and shell lines that went around a journal that did not answer are named once, in one red mark in the chat of the agent the journal next answers, and taken off the log."""

    def __init__(self, log: BypassLog, cards: MomentCards) -> None:
        self.log, self.cards = log, cards

    def handle(self, event: AgentEvent) -> None:
        bypasses = self.log.removed()
        if bypasses:
            detail = "\n".join(bypass.described() for bypass in bypasses)
            self.cards.show(event.environment_id, event.session, self.label(bypasses), detail=detail, shows=CardType.FAULTS, outcome=CardOutcome.WARNED)

    @staticmethod
    def label(bypasses: list[Bypass]) -> str:
        return "The journal was too slow to check some of the agent's work"
