from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class PlanAgentWriteScope:
    """The project root and worktree a Plan agent may write inside."""

    root: Path
    worktree: Path
