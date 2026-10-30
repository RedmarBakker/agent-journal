from dataclasses import dataclass
import math


@dataclass(frozen=True)
class SimulationCaps:
    max_runs: int
    max_processes: int
    max_storage_bytes: int
    batch_deadline_seconds: float
    run_deadline_seconds: float
    max_simulated_minutes: int

    def __post_init__(self) -> None:
        if any(not isinstance(value, int) or isinstance(value, bool) or value <= 0 for value in (
            self.max_runs, self.max_processes, self.max_storage_bytes, self.max_simulated_minutes,
        )):
            raise ValueError("run, process, storage and simulated-minute caps must be positive integers")
        if any(not math.isfinite(value) or value <= 0 for value in (self.batch_deadline_seconds, self.run_deadline_seconds)):
            raise ValueError("batch and run deadline caps must be finite and positive")
