from journal.db.query import Query
from journal.http.controllers.controller import Controller
from journal.models.test_turn import TestTurn
from journal.models.test_turn_state import TestTurnState
from journal.repositories.test_turns import TestTurns


class TestTurnController(Controller[TestTurn]):
    """The workers' turns to run tests under the test budget that have not ended: those running and those waiting for a free run."""

    __test__ = False

    repository: TestTurns

    def __init__(self, turns: TestTurns) -> None:
        self.repository = turns

    def list_query(self) -> Query:
        return self.repository.query().filter_unequal("state", TestTurnState.ENDED)
