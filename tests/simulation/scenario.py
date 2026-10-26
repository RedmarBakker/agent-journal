from dataclasses import dataclass


@dataclass(frozen=True)
class Scenario:
    """One situation a simulation plays: the work mode, how many simulated minutes, the tasks open at the start, how many messages an hour the user sends, how long a worker takes over a task, the agent's policy by name, and how many of the engine's own moments an hour it plays (EngineEvents)."""

    name: str
    mode: str
    minutes: int
    tasks: int
    user_messages_hourly: float
    worker_seconds: int
    policy: str
    engine_events_hourly: float = 0.0
