from dataclasses import dataclass
from typing import ClassVar

from journal.models.scoped import Scoped
from journal.models.test_outcome import TestOutcome
from journal.models.test_turn_state import TestTurnState


@dataclass(frozen=True)
class TestTurn(Scoped):
    """A worker's turn to run tests: the worker, the test ids it named, the command that runs them, the worktree it runs in, where it stands, the number of the output of its run once that moved to the background, and how the run came out with how many of its tests failed. Stored on this machine."""

    __test__ = False

    shared: ClassVar[bool] = False
    timeline_visible: ClassVar[bool] = False

    worker: int = 0
    ids: str = ""
    command: str = ""
    folder: str = ""
    state: TestTurnState = TestTurnState.WAITING
    output: int = 0
    outcome: TestOutcome = TestOutcome.UNKNOWN
    failed: int = 0

    def started(self) -> "TestTurn":
        return self.with_(state=TestTurnState.RUNNING)

    def ended(self) -> "TestTurn":
        return self.with_(state=TestTurnState.ENDED)

    def backgrounded(self, output: int) -> "TestTurn":
        return self.with_(output=output)

    def passed_run(self) -> "TestTurn":
        return self.with_(outcome=TestOutcome.PASSED, failed=0)

    def failed_run(self, failed: int) -> "TestTurn":
        return self.with_(outcome=TestOutcome.FAILED, failed=failed)
