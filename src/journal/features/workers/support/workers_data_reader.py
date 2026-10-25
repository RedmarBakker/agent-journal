from journal.features.workers.support.tool_use_counts import ToolUseCounts
from journal.repositories.edits import Edits
from journal.engine.support.lazy_facts import LazyFacts
from journal.repositories.scope import Scope
from journal.support.stage_times import StageTimes
from journal.config import Config
from journal.features.workers.support.worker_branch import WorkerBranch
from journal.features.workers.support.worker_worktree import WorkerWorktree
from journal.features.workers.support.ready_work import ReadyWork
from journal.models.agent import Agent
from journal.models.support.ref import Ref
from journal.repositories.command_outputs import CommandOutputs
from journal.models.proof_state import ProofState
from journal.repositories.proofs import Proofs
from journal.repositories.tasks import Tasks
from journal.support.actor import Actor
from journal.repositories.worker_todos import WorkerTodos
from journal.repositories.workers import Workers
from journal.repositories.subagents import Subagents


ACTED = (ProofState.CHECKED, ProofState.CHECKED_UNFINISHED, ProofState.SHORT)

class WorkersDataReader:
    """Reads the workers feature's part of the feature data for an agent, each fact the first time a listener asks for it, with the fields WorkersData names."""

    def __init__(self, workers: Workers, subagents: Subagents, config: Config, branch: WorkerBranch, tasks: Tasks, todos: WorkerTodos, outputs: CommandOutputs, proofs: Proofs, edits: Edits, scope: Scope, stages: StageTimes) -> None:
        self.edits, self.scope, self.stages = edits, scope, stages
        self.workers, self.subagents, self.config, self.branch, self.tasks, self.todos, self.outputs, self.proofs = workers, subagents, config, branch, tasks, todos, outputs, proofs

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
            "worktrees": lambda: tuple(WorkerWorktree(self.branch.folder(w).name, w.row_id, w.name) for w in self.workers.scoped()),
            "session_workers": lambda: tuple(self.workers.session_worker(agent.session)) if agent.role.is_sent() else (),
            "ready_work": lambda: tuple(ReadyWork(w.id, w.name, task, w.silence.timeout.start) for w in self.workers.delivered_workers() if not w.in_review for task in self.tasks.holder_task_ids(Ref.build(w))[:1] if self.is_unchecked(task)),
            "unfinished_outputs": lambda: tuple(output.row_id for worker in facts.session_workers for output in self.outputs.unfinished(Actor.worker(worker.id))),
            "todos": lambda: tuple(item for worker in facts.session_workers for task_id in self.tasks.holder_task_ids(Ref.build(worker)) for item in self.todos.task_items(self.tasks.find(task_id))),
            "tool_uses": lambda: ToolUseCounts.counted(agent),
            "code_lines": lambda: self.edits.code_line_count(agent.session, facts.tool_uses.last_handover_at),
        }, lambda: self.scope.environment(agent.environment_id), self.stages)
        return facts
