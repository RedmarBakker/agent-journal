from journal.chat.moment_cards import MomentCards
from journal.events.agent.agent_event import AgentEvent
from journal.events.listener import Listener
from journal.features.health.support.bypass import HOOK, SHELL, Bypass
from journal.features.health.support.bypass_log import BypassLog
from journal.support.card_kind import CardKind


class BypassNotice(Listener[AgentEvent]):
    """The hooks and shell lines that went around a journal that did not answer are named once, in one red mark in the chat of the agent the journal next answers, and taken off the log."""

    def __init__(self, log: BypassLog, cards: MomentCards) -> None:
        self.log, self.cards = log, cards

    def handle(self, event: AgentEvent) -> None:
        bypasses = self.log.taken()
        if bypasses:
            detail = "\n".join(bypass.described() for bypass in bypasses)
            self.cards.show(event.environment_id, event.session, self.label(bypasses), "bolt", tone="bad", detail=detail, shows=CardKind.FAULTS)

    @staticmethod
    def label(bypasses: list[Bypass]) -> str:
        hooks = sum(1 for bypass in bypasses if bypass.kind == HOOK)
        lines = sum(1 for bypass in bypasses if bypass.kind == SHELL)
        counts = [f"{hooks} {'hook' if hooks == 1 else 'hooks'} let the tool go on unchecked" if hooks else "", f"{lines} shell {'command' if lines == 1 else 'commands'} ran in the shell itself, unrecorded" if lines else ""]
        return f"The journal did not answer in time: {' and '.join(count for count in counts if count)}"
