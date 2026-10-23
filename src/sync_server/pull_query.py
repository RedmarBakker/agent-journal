from dataclasses import dataclass

from sync_server.pool_slots import PoolSlots


@dataclass(frozen=True)
class PullQuery:
    """What a pull asks: the changes past the sequence the device holds, how long it may wait for one, the environments it hosts, the pool slots it offers, and the journal version it runs."""

    sequence: int
    wait_seconds: float
    environment_keys: tuple[str, ...]
    pool: PoolSlots
    version: str

    @classmethod
    def parsed(cls, query: dict[str, str]) -> "PullQuery":
        keys = tuple(key for key in query.get("keys", "").split(",") if key)
        pool = PoolSlots(int(query.get("slots", "0")), int(query.get("free", "0")))
        return cls(int(query.get("after", "0")), float(query.get("wait", "0")), keys, pool, query.get("version", ""))
