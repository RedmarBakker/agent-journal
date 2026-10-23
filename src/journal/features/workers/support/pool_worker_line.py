from dataclasses import dataclass


@dataclass(frozen=True)
class PoolWorkerLine:
    """One pool worker as the Team page lists it: the team server's request number, the worker's number and name, the task it works on, and the person it runs for or the machine it runs on."""

    request: int
    worker: int
    name: str
    task: str
    owner: str
