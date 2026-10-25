from dataclasses import dataclass


@dataclass(frozen=True)
class StartedPlan:
    """The plan started here as the plans feature reads it: the task it would start next, the task of it in hand with its briefing, its tasks changed most recently, among them the task an event of a task of it names, how many are left, whether it stands at a phase end it waits at, a checkpoint or one whose testing commands have not passed since, which those commands are and whether it is a checkpoint, how its testing template says to test, empty when it has none, the phase in hand, and the phase and moment its orchestrator last gave its priorities."""

    plan_id: int
    next_task: int
    started_task: int
    started_task_briefing: str
    recent_tasks: tuple[int, ...]
    remaining_tasks: int
    checkpoint_pause: bool
    checkpoint_phase: int
    testing: str
    phase_commands: tuple[str, ...] = ()
    is_checkpoint: bool = False
    current_phase: int = 1
    priorities_phase: int = 0
    priorities_at: float = 0.0
