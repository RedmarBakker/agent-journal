from dataclasses import dataclass, field

from journal.models.support.agent_load import AgentLoad
from pathlib import Path

from journal.features.workers.support.merge_check import MergeCheck
from journal.features.workers.support.tool_use_counts import ToolUseCounts
from journal.features.workers.support.worker_worktree import WorkerWorktree
from journal.models.subagent import Subagent
from journal.features.workers.support.ready_work import ReadyWork
from journal.models.worker import Worker
from journal.models.worker_todo import WorkerTodo


@dataclass(frozen=True)
class WorkersData:
    """The workers feature's reading: the workers out and the idle workers whose report is not acted on, by name, profile and the files they touched, how many subagents of this session's rows are running, every subagent this session dispatched, the worktrees of the workers still at work or idle, the clocked-out workers' work waiting to be checked, those workers and the outputs, by number with their worker's, that ran in their worktrees, and, for a worker's own agent, its worker, the to-do items of the task it holds and its own outputs not yet ended; the merges the whole suite has not passed since; the agent's own load as last measured; and each worker's queue, the tasks it takes next in order."""

    dispatched_workers: tuple[Worker, ...]
    idle_workers: tuple[Worker, ...]
    active_subagents: int
    subagents: tuple[Subagent, ...]
    worktrees_root: Path
    worktrees: tuple[WorkerWorktree, ...]
    session_workers: tuple[Worker, ...] = ()
    todos: tuple[WorkerTodo, ...] = ()
    unfinished_outputs: tuple[int, ...] = ()
    ready_work: tuple[ReadyWork, ...] = ()
    delivered_workers: tuple[Worker, ...] = ()
    delivered_runs: tuple[tuple[int, int], ...] = ()
    tool_uses: ToolUseCounts = ToolUseCounts()
    code_lines: int = 0
    load: AgentLoad = AgentLoad()
    merge_check: MergeCheck = MergeCheck()
    last_calls: dict[int, str] = field(default_factory=dict)
    resumable: tuple[int, ...] = ()
    queues: dict[int, tuple[int, ...]] = field(default_factory=dict)
