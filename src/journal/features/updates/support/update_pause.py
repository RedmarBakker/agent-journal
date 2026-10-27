from dataclasses import dataclass, replace

UPDATE_PAUSE_SECONDS = 900.0


@dataclass(frozen=True)
class UpdatePause:
    """An update under way, as its mark says: the version it moves from and to, the step it is on, when it began and the process that runs it."""

    step_name: str
    target: str
    step: str
    time: float
    pid: int

    def step_pause(self, step: str) -> "UpdatePause":
        return replace(self, step=step)

    def is_stale(self, time: float) -> bool:
        return time - self.time > UPDATE_PAUSE_SECONDS

    def is_pending(self, version: str, pid: int, time: float) -> bool:
        return self.target != version and self.pid == pid and not self.is_stale(time)

    def with_process(self, pid: int, time: float, step: str) -> "UpdatePause":
        return replace(self, pid=pid, time=time, step=step)
