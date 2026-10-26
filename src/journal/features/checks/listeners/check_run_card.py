from journal.chat.process_cards import ProcessCards
from journal.events.listener import Listener
from journal.events.rows.check_run_changed import CheckRunChanged
from journal.features.checks.support.check_run_process_card import CheckRunProcessCard
from journal.repositories.agents import Agents
from journal.repositories.checks import Checks
from journal.repositories.scope import Scope


class CheckRunCard(Listener[CheckRunChanged]):
    """A check's run is a card in the chat of each live main agent from the moment it starts, written again as it ends; a check a task waits on is named by the wait's own end instead."""

    def __init__(self, card: CheckRunProcessCard, cards: ProcessCards, checks: Checks, agents: Agents, scope: Scope) -> None:
        self.card, self.cards, self.checks, self.agents, self.scope = card, cards, checks, agents, scope

    def handle(self, event: CheckRunChanged) -> None:
        if event.wait_target:
            return
        check = self.checks.find(event.check_id)
        for agent in self.agents.active_main_agents():
            with self.scope.environment(agent.environment_id):
                self.cards.show(self.card.card_contents(check, event.run_start, agent))
