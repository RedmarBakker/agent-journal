from dataclasses import dataclass

from journal.engine.nudge import Nudge


@dataclass(frozen=True)
class StartedPlan:
    """The plan started here as the plans feature reads it: the task it would start next, the task of it in hand with its briefing, its tasks, how many are left, whether it stands at a checkpoint, and how its testing template says to test, empty when it has none."""

    plan_id: int
    next_task: int
    started_task: int
    started_task_briefing: str
    tasks: tuple[int, ...]
    remaining_tasks: int
    checkpoint_pause: bool
    checkpoint_phase: int
    testing: str

    def testing_lines(self, nudge: Nudge) -> tuple[Nudge, ...]:
        return (nudge.create(n=self.plan_id, testing=self.testing),) if self.testing else ()
