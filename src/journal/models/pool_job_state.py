from enum import StrEnum


class PoolJobState(StrEnum):
    """Where a worker the team's pool offered this machine stands: waiting to be taken up, started here, turned down, or done."""

    WAITING = "waiting"
    STARTED = "started"
    DECLINED = "declined"
    FINISHED = "finished"
