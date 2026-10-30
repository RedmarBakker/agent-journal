import shlex
from argparse import Namespace

from journal.console.command import Command
from journal.features.workers.support.test_selection import TestSelection
from journal.features.workers.support.test_turns import TestTurns
from journal.features.workers.support.worker_branch import WorkerBranch
from journal.repositories.workers import Workers
from journal.support.caller import Caller
from journal.support.rejection import Rejection


class WorkerTestsCommand(Command):
    """journal tests as a worker runs it: single named tests queued with the journal, which runs them in its place, one run at a time across all workers."""

    noun = "tests"

    __test__ = False

    def __init__(self, turns: TestTurns, workers: Workers, branch: WorkerBranch) -> None:
        self.turns, self.workers, self.branch = turns, workers, branch

    def arguments(self, verbs) -> None:
        self.verb(verbs, "turn", "queue single named tests to be run for you; they run in your worktree once a run is free, one run at a time").add_argument("ids", nargs="+", help="the test ids to run, each a file or a test in one, never a folder")

    def turn(self, args: Namespace, caller: Caller) -> int:
        worker = self.workers.find(caller.worker_number)
        folders = TestSelection(tuple(args.ids)).folders(self.branch.place(worker))
        if folders:
            raise Rejection(f"queue single named tests, a file or a test in one, never a folder or a glob: {' '.join(folders)}")
        print(self.turns.run_batches(worker, shlex.join(args.ids), caller))
        return 0
