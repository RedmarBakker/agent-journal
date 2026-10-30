from dataclasses import dataclass


@dataclass(frozen=True)
class Scenario:
    """One situation a simulation plays: the work mode, how many simulated minutes, the tasks open at the start, how many messages an hour the user sends, how long a worker takes over a task, the agent's policy by name, how many of the engine's own moments an hour it plays (EngineEvents), the tasks that arrive later by minute, the deciles of a worker's job in minutes in place of the fixed length, the shares of jobs sent back once, twice and three times, how many other clocked-out workers a merge sends back as clashed, and the minute the work mode switches and to what (none at minute 0)."""

    name: str
    mode: str
    minutes: int
    tasks: int
    user_messages_hourly: float
    worker_seconds: int
    policy: str
    engine_events_hourly: float = 0.0
    arrivals: tuple[tuple[int, int], ...] = ()
    job_minutes: tuple[float, ...] = ()
    send_backs: tuple[float, ...] = ()
    clashes_per_merge: int = 0
    switch_minute: int = 0
    switch_mode: str = ""
