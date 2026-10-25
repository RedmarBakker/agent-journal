from dataclasses import dataclass
from typing import ClassVar

from journal.models.scoped import Scoped
from journal.models.test_turn_state import TestTurnState


@dataclass(frozen=True)
class TestTurn(Scoped):
    """A worker's turn to run tests: the worker, the test ids it named, the command that runs them, the worktree it runs in, where it stands, and the number of the output of its run once that moved to the background. Stored on this machine."""

    __test__ = False

    shared: ClassVar[bool] = False
    timeline_visible: ClassVar[bool] = False

    worker: int = 0
    ids: str = ""
    command: str = ""
    folder: str = ""
    state: TestTurnState = TestTurnState.WAITING
    output: int = 0

    def started(self) -> "TestTurn":
        return self.with_(state=TestTurnState.RUNNING)

    def ended(self) -> "TestTurn":
        return self.with_(state=TestTurnState.ENDED)

    def backgrounded(self, output: int) -> "TestTurn":
        return self.with_(output=output)
