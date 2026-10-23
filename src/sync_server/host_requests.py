from dataclasses import replace

from sync_server.change_log import ChangeLog
from sync_server.db.host_request_rows import HostRequestRows
from sync_server.db.pool_capacity_rows import PoolCapacityRows
from sync_server.device_ask_request import DeviceAskRequest
from sync_server.devices import Devices
from sync_server.host_ask_request import HostAskRequest
from sync_server.host_request import HostRequest
from sync_server.host_request_draft import HostRequestDraft
from sync_server.host_request_list import HostRequestList
from sync_server.pool_ask_request import PoolAskRequest
from sync_server.pool_capacity import PoolCapacity
from sync_server.pull_query import PullQuery
from sync_server.refusal import Refusal
from sync_server.request_audience import RequestAudience

POOL_WAIT_SECONDS = 600
UNCLAIMED = "pool_unclaimed"
OFFLINE_MACHINE = "pool_machine_offline"


class HostRequests:
    """Writes and jobs asked of other machines by any journal of the team, stored until a machine has made them, each for the person who asked, or for the person the hosted journal names as signed in to it. A request goes to its environment's host, to one device, or to the pool: a pool request is offered to every machine with a free slot on the version it names, taken by the one that claims it first, offered again when a machine declines it, answered back to its environment's host as pool_unclaimed when nobody claims it in ten minutes, and as pool_machine_offline when the machine that claimed it has not pulled for ten minutes before it ended. A new request wakes the waiting pulls, and each pull names the environments its machine hosts and the pool slots it offers. A host that has made a write a person asked of it may send that person's writes from then on."""

    def __init__(self, rows: HostRequestRows, capacities: PoolCapacityRows, devices: Devices, log: ChangeLog) -> None:
        self.rows, self.capacities, self.devices, self.log = rows, capacities, devices, log

    def created(self, token: str, request: HostAskRequest, created_at: float) -> HostRequestList:
        return self.added(token, HostRequestDraft(request.environment_key, request.kind, request.body, request.account_id, created_at))

    def pooled(self, token: str, request: PoolAskRequest, created_at: float) -> HostRequestList:
        return self.added(token, HostRequestDraft(request.environment_key, request.kind, request.body, request.account_id, created_at, RequestAudience.POOL, version=request.version))

    def addressed(self, token: str, request: DeviceAskRequest, created_at: float) -> HostRequestList:
        return self.added(token, HostRequestDraft(request.environment_key, request.kind, request.body, request.account_id, created_at, RequestAudience.DEVICE, request.device_id))

    def added(self, token: str, draft: HostRequestDraft) -> HostRequestList:
        person = self.devices.person(token)
        owned = draft if person.is_relay() else replace(draft, account_id=person.id)
        request = owned.numbered(self.rows.insert(owned))
        self.log.wake()
        return HostRequestList((request,))

    def waiting(self, device_id: int, query: PullQuery) -> tuple[HostRequest, ...]:
        return tuple(HostRequest.stored(row) for row in self.rows.waiting(device_id, query.environment_keys, query.pool.free, query.version))

    def store_capacity(self, device_id: int, query: PullQuery, reported_at: float) -> None:
        self.capacities.save(PoolCapacity(device_id, query.pool.slots, query.pool.free, query.version, reported_at))

    def claimed(self, token: str, id: int) -> HostRequestList:
        if not self.rows.claim(id, self.devices.device(token).id):
            raise Refusal(f"request {id} is taken by another machine or done")
        return HostRequestList(())

    def declined(self, token: str, id: int) -> HostRequestList:
        self.rows.decline(id, self.devices.device(token).id)
        self.log.wake()
        return HostRequestList(())

    def lapse(self, moment: float) -> None:
        unclaimed = [HostRequest.stored(row) for row in self.rows.unclaimed_pool(moment - POOL_WAIT_SECONDS)]
        offline = [HostRequest.stored(row) for row in self.rows.offline_claims(moment - POOL_WAIT_SECONDS)]
        for kind, requests in ((UNCLAIMED, unclaimed), (OFFLINE_MACHINE, offline)):
            for request in requests:
                self.host_reply(request, kind, moment)
        if unclaimed or offline:
            self.log.wake()

    def host_reply(self, request: HostRequest, kind: str, moment: float) -> None:
        self.rows.finish(request.id, 0, moment)
        self.rows.insert(HostRequestDraft(request.environment_key, kind, {"request": request.id, "kind": request.kind, "body": request.body}, request.account_id, moment))

    def finished(self, token: str, id: int, finished_at: float) -> HostRequestList:
        self.rows.finish(id, self.devices.person(token).id, finished_at)
        return HostRequestList(())

    def is_vouched(self, host_id: int, account_id: int) -> bool:
        return self.rows.is_vouched(host_id, account_id)
