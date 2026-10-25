from dataclasses import replace

from sync_server.account import Account
from sync_server.change_log import ChangeLog
from sync_server.db.store import Store
from sync_server.devices import Devices
from sync_server.file_store import FileStore
from sync_server.host_requests import HostRequests
from sync_server.logged_change import LoggedChange
from sync_server.push_answer import PushAnswer
from sync_server.push_request import PushRequest
from sync_server.push_results import PushResults
from sync_server.pushed_change import PushedChange
from sync_server.refusal import Refusal
from sync_server.rejected_field import RejectedField
from sync_server.row_settlement import RowSettlement
from sync_server.settlement import Settlement

USER_PREFIX = "user:"


class PushHandler:
    """Takes one device's queued changes in order: each is stamped with the person whose device sent it, never with what the request says, its times put on the server's clock by the device's offset, and its fields settled against the row as the server holds it. A change that names another person as its writer refuses the whole push before anything is stored, unless the device is the hosted journal or the host that made a write that person asked of it; a change the device sent before, known by its local number, is answered as it was the first time and stored once. A withdrawn row's files are removed once its withdrawal is stored."""

    def __init__(self, store: Store, log: ChangeLog, devices: Devices, results: PushResults, requests: HostRequests, files: FileStore) -> None:
        self.store, self.log, self.devices, self.results, self.requests, self.files = store, log, devices, results, requests, files

    def answer(self, token: str, request: PushRequest, received_at: float) -> PushAnswer:
        device, person = self.devices.device(token), self.devices.person(token)
        changes = [(change.local_number, self.stamped(change, person, device.id, request.clock_offset)) for change in request.changes]
        numbered = [local_number for local_number, _ in changes if local_number]
        if numbered:
            self.results.drop_older(device.id, min(numbered))
        settlements = [self.outcome(device.id, local_number, change) for local_number, change in changes]
        for _, change in changes:
            if change.is_withdrawal():
                self.files.removed(change.row_table, change.row)
        return PushAnswer(tuple(settlement.change.sequence for settlement in settlements), tuple(field for settlement in settlements for field in settlement.rejected), received_at)

    def stamped(self, change: PushedChange, person: Account, device_id: int, clock_offset: float) -> LoggedChange:
        if not self.may_send(change, person):
            raise Refusal(f"a change names {change.actor} as its writer, but this device is {person.name}'s: a person sends only their own writes")
        return change.logged_change(person.id, device_id, clock_offset)

    def may_send(self, change: PushedChange, person: Account) -> bool:
        if person.is_relay() or not change.actor.startswith(USER_PREFIX):
            return True
        writer = int(change.actor.removeprefix(USER_PREFIX))
        return writer == person.id or self.requests.is_vouched(person.id, writer)

    def outcome(self, device_id: int, local_number: int, change: LoggedChange) -> Settlement:
        with self.store.transaction():
            first_answer = self.results.first_answer(device_id, local_number, change) if local_number else None
            if first_answer is not None:
                return first_answer
            settlement = self.settlement(change)
            if local_number:
                self.results.record(device_id, local_number, settlement)
            return settlement

    def settlement(self, change: LoggedChange) -> Settlement:
        settlement = RowSettlement.outcome(change, self.log.row(change.row_table, change.row), self.log.is_deleted(change.row_table, change.row))
        rejected = tuple(self.add_writer_name(field) for field in settlement.rejected)
        if settlement.is_empty():
            return Settlement(settlement.change, rejected)
        return Settlement(self.log.appended(settlement.change), rejected)

    def add_writer_name(self, field: RejectedField) -> RejectedField:
        return replace(field, writer=self.devices.accounts.find(int(field.writer)).name) if field.writer else field
