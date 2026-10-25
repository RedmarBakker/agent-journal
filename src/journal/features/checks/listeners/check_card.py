from journal.support.card_outcome import CardOutcome
from journal.chat.moment_cards import MomentCards
from journal.events.listener import Listener
from journal.events.rows.check_completed import CheckCompleted
from journal.models.support.ref import Ref
from journal.repositories.agents import Agents
from journal.support.card_kind import CardKind

TAIL_LINES = 20


class CheckCard(Listener[CheckCompleted]):
    """A check that ran is one mark in the chat of each live agent, with the end of what it printed; a check a task waits on is named by the wait's own end instead."""

    def __init__(self, cards: MomentCards, agents: Agents) -> None:
        self.cards, self.agents = cards, agents

    def handle(self, event: CheckCompleted) -> None:
        if event.wait_target:
            return
        tail = "\n".join(event.output.strip().splitlines()[-TAIL_LINES:])
        for agent in self.agents.active_main_agents():
            self.cards.show(agent.environment_id, agent.session, f"Check {event.title} {'passed' if event.passed else 'failed'}", tail, Ref("checks", event.check_id), shows=CardKind.CHECKS, outcome=CardOutcome.PASSED if event.passed else CardOutcome.FAILED)
