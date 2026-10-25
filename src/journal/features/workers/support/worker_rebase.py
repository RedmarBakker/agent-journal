import time

from journal.features.workers.support.clash_return import ClashReturn
from journal.features.workers.support.worker_actions import WorkerActions
from journal.features.workers.support.worker_branch import REBASE_STEPS, WorkerBranch
from journal.models.support.ref import Ref
from journal.models.worker import Worker
from journal.repositories.tasks import Tasks
from journal.repositories.workers import Workers
from journal.support.actor import Actor


class WorkerRebase:
    """The journal rebases workers' worktrees onto the project's branch on the agent's order, never the worker: one out on a task rebases at its next clock-out, any other at once; with force a running worker is rebased at once, its writes held while the journal stashes its changes, rebases and takes them back; a clash goes back to the worker to fix, and each rebase is one mark in the chat."""

    def __init__(self, workers: Workers, tasks: Tasks, branch: WorkerBranch, actions: WorkerActions, clashes: ClashReturn) -> None:
        self.workers, self.tasks, self.branch, self.actions, self.clashes = workers, tasks, branch, actions, clashes

    def rebase(self, worker: Worker, actor: Actor) -> str:
        if worker.is_running() and self.tasks.holder_task_ids(Ref.build(worker)):
            self.workers.save(worker.with_(rebase_due=True), actor)
            return f"worker {worker.id}, {worker.name}: rebased at its next clock-out, once its current task is done"
        return self.immediate_rebase(worker, actor)

    def immediate_rebase(self, worker: Worker, actor: Actor) -> str:
        return self.running_rebase(worker, actor) if worker.is_running() else self.resting_rebase(worker, actor)

    def running_rebase(self, worker: Worker, actor: Actor) -> str:
        try:
            clashing = self.branch.rebased_onto_branch(self.workers.save(worker.with_(edit_lock=True), actor))
            heads = self.branch.project_heads(worker)
        finally:
            self.workers.save(self.workers.find(worker.id).with_(edit_lock=False), actor)
        self.workers.save(self.workers.find(worker.id).rebased(self.outcome(heads, clashing), time.time()), actor)
        return f"worker {worker.id}, {worker.name}: {self.outcome(heads, clashing)}" + self.delivery(worker, self.worker_line(heads, clashing), actor)

    def delivery(self, worker: Worker, line: str, actor: Actor) -> str:
        refusal = self.actions.notify_refusal(worker)
        if refusal:
            return f"; it was not told, since {refusal.format(n=worker.id, name=worker.name, provider=worker.provider.capitalize())}"
        self.actions.notify(worker.id, line, actor)
        return ""

    def resting_rebase(self, worker: Worker, actor: Actor) -> str:
        clashing = self.branch.rebased_onto_branch(worker)
        outcome = self.outcome(self.branch.project_heads(worker), clashing)
        self.workers.save(self.workers.find(worker.id).rebased(outcome, time.time()), actor)
        if clashing:
            self.clashes.send(self.workers.find(worker.id), clashing)
        return f"worker {worker.id}, {worker.name}: {outcome}"

    @staticmethod
    def outcome(heads: str, clashing: str) -> str:
        return f"its worktree rebased onto the project's branch, at {heads}" + (f", and {clashing}" if clashing else "")

    @staticmethod
    def worker_line(heads: str, clashing: str) -> str:
        if clashing:
            return f"The journal rebased your worktree onto the project's branch, at {heads}, and {clashing}. {REBASE_STEPS}, then go on with your task."
        return f"The journal rebased your worktree onto the project's branch, at {heads}, so files may have changed under you; your own changes are kept. Go on with your task."
