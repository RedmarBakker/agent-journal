from journal.features.workers.support.worker_branch import WorkerBranch
from journal.features.workers.support.worker_task_assigner import WorkerTaskAssigner
from journal.models.proof_state import ProofState
from journal.models.support.ref import Ref
from journal.models.task import Task
from journal.models.task_state import TaskState
from journal.models.worker import Worker
from journal.repositories.proofs import Proofs
from journal.repositories.tasks import Tasks
from journal.repositories.workers import Workers
from journal.support.caller import Caller
from journal.support.time_source import TimeSource


class QueueAdvance:
    """A worker's move to the next task of its queue: made as the last point of the task in hand is proved, while a task is queued, it is not blocked and no point is proved not done; the work is committed and the worker goes on in the same session, with no report and no test run until its queue is done."""

    def __init__(self, workers: Workers, tasks: Tasks, proofs: Proofs, branch: WorkerBranch, assigner: WorkerTaskAssigner, time_source: TimeSource) -> None:
        self.workers, self.tasks, self.proofs, self.branch, self.assigner, self.time_source = workers, tasks, proofs, branch, assigner, time_source

    def next_task(self, worker: Worker, task: Task) -> Task | None:
        waiting = self.tasks.queue(Ref(Worker.table(), worker.id))
        if not waiting or waiting[0].state == TaskState.BLOCKED or self.is_unfinished(task):
            return None
        return waiting[0]

    def advanced(self, worker: Worker, task: Task, following: Task, caller: Caller) -> None:
        self.branch.commit_changes(worker, f"Task {task.id}: {task.title}")
        self.tasks.finish_holder_task(task.id, Ref(Worker.table(), worker.id), caller.actor)
        next_task = self.assigner.handed(worker, following, caller.actor)
        self.workers.save(self.workers.find(worker.id).queue_advanced(next_task.id, self.time_source.moment().timestamp()), caller.actor)
        print(f"task {task.id} is done and waits to be checked and merged with the rest of your queue; your next task, {next_task.id}: {next_task.title}. {next_task.brief}")
        print("work on it now in this session and prove each of its points; the journal commits your work as you prove the last point, and you clock out once, when your queue is done, naming there the tests of every task")

    def is_unfinished(self, task: Task) -> bool:
        return any(proof.state == ProofState.UNFINISHED for proof in self.latest_proofs(task).values())

    def unproved(self, task: Task) -> list[int]:
        latest = self.latest_proofs(task)
        return [point for point in range(1, len(task.points()) + 1) if point not in latest or latest[point].state in (ProofState.SHORT, ProofState.STALE)]

    def latest_proofs(self, task: Task) -> dict:
        return {proof.point: proof for proof in sorted(self.proofs.task_proofs(task), key=lambda proof: proof.row_id)}
