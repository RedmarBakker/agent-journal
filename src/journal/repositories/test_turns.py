from journal.models.test_turn import TestTurn
from journal.models.test_turn_state import TestTurnState
from journal.repositories.scoped_repository import ScopedRepository


class TestTurns(ScopedRepository[TestTurn]):
    __test__ = False

    model = TestTurn

    def waiting(self) -> list[TestTurn]:
        return self.selected_globally(self.query().filter(state=TestTurnState.WAITING).order("id"))

    def running(self) -> list[TestTurn]:
        return self.selected_globally(self.query().filter(state=TestTurnState.RUNNING).order("id"))

    def of_output(self, output: int) -> list[TestTurn]:
        return self.selected_globally(self.query().filter(output=output).order("id").limit(1))
