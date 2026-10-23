from typing import Callable

from journal.features.workers.support.pool_worker_moves import CLEANUP, NOTE, REDO, STOPPED, PoolWorkerMoves
from journal.features.workers.support.worker_branch import WorkerBranch
from journal.features.workers.support.worker_runner import WorkerRunner
from journal.features.workers.support.worker_actions import REDO_MOVE, WorkerActions
from journal.models.worker import Worker
from journal.models.worker_state import WorkerState
from journal.repositories.environments import Environments
from journal.repositories.scope import Scope
from journal.repositories.workers import Workers
from journal.support.actor import Actor
from journal.support.host_writer import HostWriter
from journal.support.rejection import Rejection
from sync_server.host_request import HostRequest


class PoolRunnerWrites(HostWriter):
    """What the journal that dispatched a pool worker asks of the machine running it: a point sent back, which resumes the worker on it, or, when it cannot be resumed, stops it and tells the dispatcher why, a word for it while it runs, and the clearing of one the dispatcher is done with: its run stopped, its slot freed and its worktree and branch dropped."""

    def __init__(self, actions: WorkerActions, workers: Workers, environments: Environments, scope: Scope, moves: PoolWorkerMoves, runner: WorkerRunner, branch: WorkerBranch) -> None:
        self.actions, self.workers, self.environments, self.scope, self.moves = actions, workers, environments, scope, moves
        self.runner, self.branch = runner, branch

    def makers(self) -> dict[str, Callable[[HostRequest], None]]:
        return {REDO: self.redo, NOTE: self.note, CLEANUP: self.cleanup}

    def redo(self, request: HostRequest) -> None:
        for environment in self.environments.keyed(request.environment_key):
            with self.scope.environment(environment.row_id):
                self.relaunched(self.workers.find(request.body["worker_id"]), request.body["brief"], Actor.user(request.account_id))

    def relaunched(self, worker: Worker, brief: str, actor: Actor) -> None:
        try:
            self.actions.relaunch(worker, brief, None, actor, REDO_MOVE)
        except Rejection as refused:
            self.moves.ask(worker, STOPPED, {"reason": f"the point sent back could not be taken up: {refused}"}, actor)

    def cleanup(self, request: HostRequest) -> None:
        for environment in self.environments.keyed(request.environment_key):
            with self.scope.environment(environment.row_id):
                self.cleared(self.workers.find(request.body["worker_id"]))

    def cleared(self, worker: Worker) -> None:
        self.runner.stop(worker)
        self.moves.ended(worker)
        self.branch.dropped(worker.with_(state=WorkerState.RELEASED))

    def note(self, request: HostRequest) -> None:
        for environment in self.environments.keyed(request.environment_key):
            with self.scope.environment(environment.row_id):
                self.actions.notified(self.workers.find(request.body["worker_id"]), request.body["text"], request.body["sender"], Actor.user(request.account_id))
