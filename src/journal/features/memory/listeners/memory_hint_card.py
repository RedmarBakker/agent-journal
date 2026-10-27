from journal.chat.moment_cards import MomentCards
from journal.events.agent.line_delivered import LineDelivered
from journal.events.agent_listener import AgentListener
from journal.repositories.reminders import Reminders
from journal.repositories.rules import Rules
from journal.support.card_type import CardType
from journal.models.support.ref import Ref
from journal.features.memory.memory_nudges import MemoryNudges

MEMORY_CHAT_KINDS = {"rule": CardType.RULES, "reminder": CardType.REMINDERS}


class MemoryHintCard(AgentListener[LineDelivered]):
    """A rule or reminder the memory conduct sent back to the agent is shown in the chat as a mark, once per line sent."""

    def __init__(self, rules: Rules, reminders: Reminders, cards: MomentCards) -> None:
        self.cards = cards
        self.repositories: dict[str, Rules | Reminders] = {"rule": rules, "reminder": reminders}

    def handle(self, event: LineDelivered) -> None:
        if event.nudge != MemoryNudges.MEMORY_READ_REQUEST.key:
            return
        noun, n = event.values["noun"], int(event.values["n"])
        row = self.repositories[noun].find(n)
        self.cards.show(event.environment_id, event.session, f"Reminded the agent about {noun} {n}", "", Ref.build(row), kind="whisper", shows=MEMORY_CHAT_KINDS[noun])
