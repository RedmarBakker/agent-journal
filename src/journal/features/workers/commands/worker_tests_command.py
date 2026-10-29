import shlex
from argparse import Namespace

from journal.console.command import Command
from journal.features.workers.support.test_turns import TestTurns
from journal.repositories.workers import Workers
from journal.support.caller import Caller


class WorkerTestsCommand(Command):
    """journal tests as a worker runs it: its turn to run tests within the test budget."""

    noun = "tests"

    __test__ = False

    def __init__(self, turns: TestTurns, workers: Workers) -> None:
        self.turns, self.workers = turns, workers

    def arguments(self, verbs) -> None:
        self.verb(verbs, "turn", "ask for a turn to run tests within the test budget; the tests run in your worktree once a run is free").add_argument("ids", nargs="+", help="the test ids to run")

    def turn(self, args: Namespace, caller: Caller) -> int:
        print(self.turns.run_batches(self.workers.find(caller.worker_number), shlex.join(args.ids), caller))
        return 0
