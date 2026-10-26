from journal.features.workers.support.merge_checks import MergeChecks
from journal.repositories.entries import Entries
from journal.engine.support.lazy_facts import LazyFacts
from journal.repositories.scope import Scope
from journal.support.stage_times import StageTimes
from journal.config import Config
from journal.features.workers.support.worker_branch import WorkerBranch
from journal.features.workers.support.worker_resumes import WorkerResumes
from journal.features.workers.support.worker_worktree import WorkerWorktree
from journal.features.workers.support.ready_work import ReadyWork
from journal.models.agent import Agent
from journal.models.support.ref import Ref
from journal.repositories.command_outputs import CommandOutputs
from journal.models.proof_state import ProofState
from journal.repositories.proofs import Proofs
from journal.repositories.tasks import Tasks
from journal.support.actor import Actor
from journal.support.command_text import CommandText
from journal.repositories.worker_todos import WorkerTodos
from journal.repositories.workers import Workers
from journal.repositories.subagents import Subagents


# how much of the worker's last tool call a quiet line quotes
LAST_CALL_CHARACTERS = 40
ACTED = (ProofState.CHECKED, ProofState.CHECKED_UNFINISHED, ProofState.SHORT)

class WorkersDataReader:
    """Reads the workers feature's part of the feature data for an agent, each fact the first time a listener asks for it, with the fields WorkersData names."""

    def __init__(self, workers: Workers, subagents: Subagents, config: Config, branch: WorkerBranch, tasks: Tasks, todos: WorkerTodos, outputs: CommandOutputs, proofs: Proofs, checks: MergeChecks, scope: Scope, stages: StageTimes, entries: Entries, resumes: WorkerResumes) -> None:
        self.checks, self.scope, self.stages, self.entries, self.resumes = checks, scope, stages, entries, resumes
        self.workers, self.subagents, self.config, self.branch, self.tasks, self.todos, self.outputs, self.proofs = workers, subagents, config, branch, tasks, todos, outputs, proofs

    def last_call(self, session: str) -> str:
        started = self.entries.tool_starts(session, 1) if session else []
        call = started[0].recorded_call() if started else None
        if call is None:
            return "no tool call yet"
        return CommandText.shortened(call.command or " ".join(filter(None, (call.work, *(call.edited_paths or call.read_paths)[:1]))) or "a tool", LAST_CALL_CHARACTERS)

    def is_unchecked(self, task_id: int) -> bool:
        latest = {proof.point: proof for proof in sorted(self.proofs.task_proofs(self.tasks.find(task_id)), key=lambda proof: proof.row_id)}
        return not latest or any(proof.state not in ACTED for proof in latest.values())

    def read(self, agent: Agent) -> LazyFacts:
        facts = LazyFacts("workers", {
            "session_subagent_rows": lambda: self.subagents.session_subagents(agent.session),
            "dispatched_workers": lambda: tuple(self.workers.running_workers()),
            "idle_workers": lambda: tuple(self.workers.idle_workers()),
            "active_subagents": lambda: sum(1 for s in facts.session_subagent_rows if s.is_running()),
            "subagents": lambda: tuple(facts.session_subagent_rows),
            "worktrees_root": lambda: (self.config.home / "worktrees").resolve(),
            "worktrees": lambda: tuple(WorkerWorktree(self.branch.folder(w).name, w.row_id, w.name) for w in (*self.workers.open_workers(), *facts.idle_workers)),
            "session_workers": lambda: tuple(self.workers.session_worker(agent.session)) if agent.role.is_helper() else (),
            "delivered_workers": lambda: tuple(self.workers.checkable_workers()),
            "delivered_runs": lambda: tuple((output.row_id, worker.row_id) for worker in facts.delivered_workers if worker.worktree for output in self.outputs.tree_runs(str(self.branch.folder(worker)))),
            "ready_work": lambda: tuple(ReadyWork(w.id, w.name, task, w.silence.timeout.start) for w in self.workers.checkable_workers() for task in self.tasks.holder_task_ids(Ref.build(w))[:1] if self.is_unchecked(task)),
            "unfinished_outputs": lambda: tuple(output.row_id for worker in facts.session_workers for output in self.outputs.unfinished(Actor.worker(worker.id))),
            "todos": lambda: tuple(item for worker in facts.session_workers for task_id in self.tasks.holder_task_ids(Ref.build(worker)) for item in self.todos.task_items(self.tasks.find(task_id))),
            "workload": lambda: agent.work_queue,
            "merge_check": lambda: self.checks.failure(),
            "last_calls": lambda: {w.id: self.last_call(w.session) for w in facts.dispatched_workers},
            "resumable": lambda: tuple(w.id for w in self.workers.unfinished_accepted(agent.session, self.resumes.is_resumable)),
            "band": lambda: agent.band,
            "band_changed_at": lambda: agent.band_changed_at,
            "measures": lambda: agent.measures,
            "queues": lambda: {worker: tuple(task.row_id for task in tasks) for worker, tasks in self.tasks.queues(self.workers.scoped()).items()},
        }, lambda: self.scope.environment(agent.environment_id), self.stages)
        return facts
