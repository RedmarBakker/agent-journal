import time
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class FrontHealth:
    """How the supervisor tells that the agent in front has lost its hooks, as its launch file says in plain data: while its terminal output keeps changing, the file its hooks write stands still past a number of seconds; then the warning given is typed to it, once until the file moves again."""

    file: str
    stale_seconds: float
    warning: str
    output_seconds: float = 30.0

    def is_dead(self, output_at: float, started_at: float) -> bool:
        moment = time.time()
        path = Path(self.file)
        modified_at = max(path.stat().st_mtime if path.is_file() else 0.0, started_at)
        return moment - output_at <= self.output_seconds and moment - modified_at > self.stale_seconds
