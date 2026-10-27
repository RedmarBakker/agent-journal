from dataclasses import dataclass


@dataclass(frozen=True)
class SupervisorProcess:
    """One process a supervisor runs, as its list answers it: its name, its process id, whether it runs, when it last started, how often it was started again, and whether it is the agent's terminal in front."""

    name: str
    pid: int
    is_running: bool
    started_at: float
    restarts: int
    front: bool

    @classmethod
    def parsed(cls, data: dict) -> "SupervisorProcess":
        return cls(str(data.get("name", "")), int(data.get("pid", 0)), bool(data.get("running")), float(data.get("started_at", 0.0)), int(data.get("restarts", 0)), bool(data.get("front")))
