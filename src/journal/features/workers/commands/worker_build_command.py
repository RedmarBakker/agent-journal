from argparse import Namespace

from journal.console.command import Command
from journal.features.workers.support.test_turns import TestTurns
from journal.repositories.workers import Workers
from journal.support.caller import Caller


class WorkerBuildCommand(Command):
    """journal build as a worker runs it: the project's build command queued with the journal, which runs it in the worker's place, one run at a time with the queued tests."""

    noun = "build"
    default_verb = "queued"

    def __init__(self, turns: TestTurns, workers: Workers) -> None:
        self.turns, self.workers = turns, workers

    def arguments(self, verbs) -> None:
        self.verb(verbs, "queued", "queue the project's build to be run for you in your worktree, once a run is free")

    def queued(self, args: Namespace, caller: Caller) -> int:
        print(self.turns.built(self.workers.find(caller.worker_number), caller))
        return 0
