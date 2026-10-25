from argparse import Namespace

from journal.console.command import WORKER_KINDS, Command
from journal.features.workers.support.worker_branch import WorkerBranch
from journal.features.workers.support.pool_worker_moves import DELIVERED, PoolWorkerMoves
from journal.features.workers.support.worker_reports import WorkerReports
from journal.models.proof_state import ProofState
from journal.models.support.ref import Ref
from journal.models.task import Task
from journal.models.worker import Worker
from journal.repositories.proofs import Proofs
from journal.repositories.tasks import Tasks
from journal.repositories.workers import Workers
from journal.support.caller import Caller
from journal.support.rejection import Rejection


class DepartureCommand(Command):
    """journal clock-out "<report>": a worker's one report, accepted only once every point of its task's brief has a valid proof and its worktree has no uncommitted file."""

    noun = "clock-out"
    default_verb = "record"
    callers = {"record": WORKER_KINDS}

    def __init__(self, workers: Workers, tasks: Tasks, proofs: Proofs, reports: WorkerReports, branch: WorkerBranch, moves: PoolWorkerMoves) -> None:
        self.workers, self.tasks, self.proofs, self.reports, self.branch, self.moves = workers, tasks, proofs, reports, branch, moves

    def arguments(self, verbs) -> None:
        self.verb(verbs, "record", "hand in your work with your report, once each point of your brief has a proof").add_argument("report")

    def record(self, args: Namespace, caller: Caller) -> int:
        if caller.worker_number is None:
            raise Rejection("only a worker clocks out: a worker's commands carry its number")
        worker = self.workers.find(caller.worker_number)
        holdings = self.tasks.holder_task_ids(Ref(Worker.table(), worker.id))
        if not holdings:
            raise Rejection(f"worker {worker.id} holds no task: a worker clocks out of the task it was sent on")
        task = self.tasks.find(holdings[0])
        missing = self.unproved(task)
        if missing:
            raise Rejection(f"point {', '.join(map(str, missing))} of task {task.id} has no proof that stands: journal proof <point> \"<file:line, and the test that shows it>\", or journal proof <point> --not-done \"<why>\"")
        uncommitted = self.uncommitted(worker)
        if uncommitted:
            raise Rejection(f"your worktree has uncommitted files, which would be lost: {', '.join(uncommitted)}; commit them first")
        if worker.pool_request:
            self.push_branch(worker)
        if self.moves.is_remote(worker):
            self.moves.ask(worker, DELIVERED, {"report": args.report}, caller.actor)
        else:
            self.reports.delivered(worker, args.report, caller.actor)
        print(f"worker {worker.id} clocked out of task {task.id}; the agent that sent you checks each proof")
        return 0

    def push_branch(self, worker: Worker) -> None:
        outcome = self.branch.git("push", "origin", f"{self.branch.name(worker)}:refs/heads/{WorkerBranch.pool_branch(worker)}", cwd=self.branch.folder(worker))
        if outcome.returncode != 0:
            raise Rejection(f"your branch could not be pushed to origin for the agent that sent you: {outcome.stderr.strip()}; fix it and clock out again")
        self.moves.ended(worker)

    def unproved(self, task: Task) -> list[int]:
        latest = {proof.point: proof for proof in sorted(self.proofs.task_proofs(task), key=lambda proof: proof.row_id)}
        return [point for point in range(1, len(task.points()) + 1) if point not in latest or latest[point].state in (ProofState.SHORT, ProofState.STALE)]

    def uncommitted(self, worker: Worker) -> list[str]:
        if not worker.worktree:
            return []
        return self.branch.remaining(worker)
