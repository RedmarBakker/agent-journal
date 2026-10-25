from typing import Callable

from sync_server.account import Account
from sync_server.accounts import Accounts
from sync_server.db.lease_rows import LeaseRows
from sync_server.db.store import Store
from sync_server.device import Device
from sync_server.lease import Lease
from sync_server.refusal import Refusal

LAPSE_SECONDS = 90
# the lapse a lease taken with none of its own is written with: it lapses after LAPSE_SECONDS as they stand when it is asked about
SERVER_LAPSE = 0
UPGRADE_LEASE = "upgrade"


class Leases:
    """Named leases, one device at a time, which know no journal concept: a device acquires a name nobody holds, or one whose holder stopped renewing it for the lapse it was taken with, or for LAPSE_SECONDS when it was taken with none of its own, renews it by acquiring it again, and lets it go; a free acquire takes only a name no other device holds, lapsed or not, so a lapsed one passes to another device only by a plain acquire, its takeover. Two devices racing for one name are settled in one transaction, so exactly one wins. While a device holds the upgrade lease, no other device may push."""

    def __init__(self, store: Store, rows: LeaseRows, accounts: Accounts) -> None:
        self.store, self.rows, self.accounts = store, rows, accounts

    def acquire(self, name: str, device: Device, person: Account, request_at: float, lapse_seconds: float = SERVER_LAPSE) -> Lease:
        return self.acquired_lease(name, device, person, request_at, lapse_seconds, Lease.excludes)

    def acquire_free(self, name: str, device: Device, person: Account, request_at: float, lapse_seconds: float = SERVER_LAPSE) -> Lease:
        return self.acquired_lease(name, device, person, request_at, lapse_seconds, Lease.has_other_holder)

    def acquired_lease(self, name: str, device: Device, person: Account, request_at: float, lapse_seconds: float, refused: Callable[[Lease, int], bool]) -> Lease:
        with self.store.transaction():
            standing = self.state(name, request_at)
            if refused(standing, device.id):
                raise Refusal(standing.refusal(request_at))
            self.rows.write(name, device.id, person.id, request_at, lapse_seconds)
            return self.state(name, request_at)

    def is_holder(self, name: str, device: Device, request_at: float) -> bool:
        standing = self.state(name, request_at)
        return standing.device_id == device.id and not standing.is_lapsed

    def require_free(self, name: str, device: Device, request_at: float) -> None:
        standing = self.state(name, request_at)
        if standing.excludes(device.id):
            raise Refusal(f"the team is upgrading on {standing.holder}'s machine: this journal's changes wait until it is done")

    def release(self, name: str, device: Device, request_at: float) -> Lease:
        with self.store.transaction():
            if self.state(name, request_at).device_id == device.id:
                self.rows.remove(name)
            return self.state(name, request_at)

    def state(self, name: str, request_at: float) -> Lease:
        row = self.rows.current(name)
        if row is None:
            return Lease(name)
        return Lease(name, row["device_id"], self.accounts.find(row["account_id"]).name, row["renewed_at"], request_at - row["renewed_at"] > self.lapse(row["lapse_seconds"]), row["device_name"])

    @staticmethod
    def lapse(lapse_seconds: float) -> float:
        return lapse_seconds if lapse_seconds != SERVER_LAPSE else LAPSE_SECONDS
