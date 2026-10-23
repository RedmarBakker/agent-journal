from dataclasses import dataclass

from sync_server.pool_slots import PoolSlots
from sync_server.pull_query import PullQuery
from sync_server.pushed_change import PushedChange


@dataclass(frozen=True)
class PushRequest:
    """A device's push: its queued changes in order, how far the server's clock is ahead of the device's, which the device measured from the server's time in its last answer, and what its pull, answered with the push, goes on from: the sequence it holds, the keys of the environments it hosts, the pool slots it offers and the journal version it runs."""

    clock_offset: float
    changes: tuple[PushedChange, ...]
    sequence: int
    environment_keys: tuple[str, ...]
    pool: PoolSlots
    version: str

    @classmethod
    def parsed(cls, changes: list, clock_offset: float = 0.0, sequence: int = 0, environment_keys: tuple = (), pool_slots: int = 0, pool_free: int = 0, version: str = "") -> "PushRequest":
        return cls(float(clock_offset), tuple(PushedChange(**change) for change in changes), int(sequence), tuple(environment_keys), PoolSlots(int(pool_slots), int(pool_free)), str(version))

    def pull_query(self) -> PullQuery:
        return PullQuery(self.sequence, 0, self.environment_keys, self.pool, self.version)
