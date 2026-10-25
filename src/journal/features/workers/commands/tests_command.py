import shlex
from argparse import Namespace

from journal.console.command import WORKER_KINDS, Command
from journal.features.workers.support.test_turns import TestTurns
from journal.repositories.workers import Workers
from journal.support.caller import Caller
from journal.support.rejection import Rejection


class TestsCommand(Command):
    __test__ = False

    noun = "tests"
    callers = {"turn": WORKER_KINDS}

    def __init__(self, turns: TestTurns, workers: Workers) -> None:
        self.turns, self.workers = turns, workers

    def arguments(self, verbs) -> None:
        self.verb(verbs, "turn", "a worker's turn to run tests within the test budget: they run in your worktree when a run is free, and the result is what the project's reader for the command picks").add_argument("ids", nargs="+", help="the test ids to run")

    def turn(self, args: Namespace, caller: Caller) -> int:
        if caller.worker_number is None:
            raise Rejection("only a worker asks for a turn to run tests: the agent that sent it runs them itself")
        print(self.turns.take(self.workers.find(caller.worker_number), shlex.join(args.ids), caller))
        return 0
