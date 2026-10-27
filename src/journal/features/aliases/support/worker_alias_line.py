from journal.features.workers.support.worker_branch import WorkerBranch
from journal.repositories.workers import Workers
from journal.support.caller import Caller

BRANCH = "--branch"


class WorkerAliasLine:
    """The arguments a worker's alias runs with: a --branch with no base after it is given the base the worker's branch is merged into, so the alias judges only what the worker changed."""

    def __init__(self, workers: Workers, branch: WorkerBranch) -> None:
        self.workers, self.branch = workers, branch

    def argv(self, argv: list[str], caller: Caller) -> list[str]:
        if not caller.is_worker() or BRANCH not in argv:
            return argv
        place = argv.index(BRANCH) + 1
        if place < len(argv) and not argv[place].startswith("-"):
            return argv
        return [*argv[:place], self.branch.base(self.workers.find(caller.worker_number)), *argv[place:]]
