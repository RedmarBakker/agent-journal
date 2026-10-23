from sync_server.db.store import Store
from sync_server.pool_capacity import PoolCapacity


class PoolCapacityRows:
    """The SQL of the pool_capacities table: the worker slots each machine gives the team's pool, one row a device."""

    def __init__(self, store: Store) -> None:
        self.store = store

    def save(self, capacity: PoolCapacity) -> None:
        self.store.execute("INSERT INTO pool_capacities (device_id, slots, free, version, reported_at) VALUES (?, ?, ?, ?, ?) ON CONFLICT (device_id) DO UPDATE SET slots = excluded.slots, free = excluded.free, version = excluded.version, reported_at = excluded.reported_at", (capacity.device_id, capacity.slots, capacity.free, capacity.version, capacity.reported_at))

    def capacities(self) -> list[PoolCapacity]:
        return [PoolCapacity.stored(row) for row in self.store.all("SELECT device_id, slots, free, version, reported_at FROM pool_capacities WHERE slots > 0 ORDER BY device_id")]
