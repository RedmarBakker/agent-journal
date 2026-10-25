from journal.chat.process_cards import ProcessCards
from journal.events.listener import Listener
from journal.events.rows.clock_out_test_run_changed import ClockOutTestRunChanged
from journal.features.workers.support.test_run_process_card import TestRunProcessCard
from journal.repositories.scope import Scope
from journal.repositories.test_turns import TestTurns


class TestRunCard(Listener[ClockOutTestRunChanged]):
    """The test run the journal makes at a worker's clock-out is a card in the chat of the agent that sent it from the moment it starts, written again as it ends."""

    __test__ = False

    def __init__(self, card: TestRunProcessCard, cards: ProcessCards, turns: TestTurns, scope: Scope) -> None:
        self.card, self.cards, self.turns, self.scope = card, cards, turns, scope

    def handle(self, event: ClockOutTestRunChanged) -> None:
        with self.scope.environment(event.environment_id):
            self.cards.show(self.card.card_contents(self.turns.find(event.turn)))
