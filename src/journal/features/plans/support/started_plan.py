from dataclasses import dataclass


@dataclass(frozen=True)
class StartedPlan:
    """The plan started here as the plans feature reads it: the task it would start next and whether any task of it can start, the task of it in hand with its briefing, its tasks changed most recently, among them the task an event of a task of it names, how many are left, whether it stands at a phase end it waits at, a checkpoint or one whose testing commands have not passed since, which those commands are and whether it is a checkpoint, how its testing template says to test, empty when it has none, the phase in hand, the phase and moment its orchestrator last gave its priorities, whether its testing refuses a test run now: always under Never run tests, and in the middle of a phase under Tests at each phase end, and whether it goes on past its checkpoints, which the task assigner decides."""

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
    refuses_test_runs: bool = False
    has_next_task: bool = False
    passes_checkpoints: bool = False
