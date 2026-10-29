import time
from dataclasses import dataclass

from journal.support.timeout import Timeout


@dataclass(frozen=True)
class PlanStatus:
    """A started plan as the orchestrator is reminded of it: its number and title, the phase in hand of how many, its tasks done of all, its open tasks no worker holds, when it last moved, and how many of its tasks are blocked."""

    plan_id: int
    title: str
    phase: int
    phases: int
    done: int
    total: int
    unassigned: int
    moved_at: float
    blocked: int = 0

    def line(self, current_time: float) -> str:
        phase = f"phase {self.phase} of {self.phases}, " if self.phases else ""
        return f"plan {self.plan_id}, {self.title}: {phase}{self.done} of {self.total} tasks done, {self.unassigned} open with no worker, last moved {int((current_time - self.moved_at) // 60)} minutes ago"

    def is_stalled(self, current_time: float, seconds: float) -> bool:
        return Timeout.seconds(seconds).started(self.moved_at).is_elapsed(current_time)

    def moved_line(self) -> str:
        return time.strftime("%Y-%m-%d %H:%M", time.localtime(self.moved_at))
