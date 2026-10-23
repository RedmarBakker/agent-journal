from sync_server.change_log import ChangeLog
from sync_server.db.host_request_rows import HostRequestRows
from sync_server.devices import Devices
from sync_server.host_ask_request import HostAskRequest
from sync_server.host_request import HostRequest
from sync_server.host_request_list import HostRequestList


class HostRequests:
    """Writes asked of an environment's host by any journal of the team, kept until the host has made them, each for the person who asked, or for the person the hosted journal names as signed in to it; a new one wakes the held pulls, and the host takes them up with its pull, which names the keys of the environments it hosts. A host that has made a write a person asked of it may send that person's writes from then on."""

    def __init__(self, rows: HostRequestRows, devices: Devices, log: ChangeLog) -> None:
        self.rows, self.devices, self.log = rows, devices, log

    def created(self, token: str, request: HostAskRequest, created_at: float) -> HostRequestList:
        person = self.devices.person(token)
        account_id = request.account_id if person.is_relay() else person.id
        number = self.rows.insert(request.environment_key, request.kind, request.body, account_id, created_at)
        self.log.wake()
        return HostRequestList((HostRequest(number, request.environment_key, request.kind, request.body, account_id, created_at),))

    def waiting(self, environment_keys: tuple[str, ...]) -> tuple[HostRequest, ...]:
        return tuple(HostRequest.stored(row) for row in self.rows.waiting(environment_keys))

    def finished(self, token: str, id: int, finished_at: float) -> HostRequestList:
        self.rows.finish(id, self.devices.person(token).id, finished_at)
        return HostRequestList(())

    def is_vouched(self, host_id: int, account_id: int) -> bool:
        return self.rows.is_vouched(host_id, account_id)
