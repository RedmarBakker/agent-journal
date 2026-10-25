from journal.features.seed import Seed
from journal.features.workers.support.test_turns import TestTurns


class TestTurnsResume(Seed):
    """At boot the test turns that waited when the server stopped start again in order, and a turn that was running without a run to wait on is over."""

    __test__ = False

    def __init__(self, turns: TestTurns) -> None:
        self.turns = turns

    def run(self) -> None:
        self.turns.resume()
