from sync_server.change_log import ChangeLog
from sync_server.devices import Devices
from sync_server.host_requests import HostRequests
from sync_server.pull_answer import PullAnswer
from sync_server.pull_query import PullQuery
from sync_server.server_clock import ServerClock
from sync_server.team_details import TeamDetails

WAIT_SECONDS = 25
TRIM_SECONDS = 60


class PullHandler:
    """Answers a device with the team's changes past the sequence it holds, not its own, in order, with the writes waiting for the environments it says it hosts, for it alone, and for the pool while it offers a free slot, its offer recorded; while neither is new it holds the request up to WAIT_SECONDS and answers the moment one arrives. The sequence it holds is recorded and the furthest it has ever named is the one answered from, so a pull that carries a sequence read before the device's other loop moved on is never told to take the full copy; and at most once a minute pool requests nobody claimed in time are answered back and the log is trimmed of the changes every device that is not revoked and has pulled is past, the lowest sequence a pull may go on from rising with it; each answer names the team's pinned version, and a held pull is answered at once when it moves; a device behind the lowest sequence a pull may go on from is told to take the full copy."""

    def __init__(self, log: ChangeLog, devices: Devices, clock: ServerClock, details: TeamDetails, requests: HostRequests) -> None:
        self.log, self.devices, self.clock, self.details, self.requests = log, devices, clock, details, requests
        self.trimmed_at = 0.0

    def answer(self, token: str, query: PullQuery) -> PullAnswer:
        device = self.devices.device(token)
        self.devices.record_pull(device, query.sequence, self.clock.time())
        self.requests.store_capacity(device.id, query, self.clock.time())
        furthest = self.devices.pulled_sequence(device)
        self.trim()
        deadline = self.clock.monotonic() + min(query.wait_seconds, WAIT_SECONDS)
        head = self.log.head()
        changes = self.log.pull_page(furthest, device.id)
        waiting = self.requests.waiting(device.id, query)
        version = self.details.version()
        while not changes and not waiting and not self.log.is_closed and self.clock.monotonic() < deadline and self.details.version() == version:
            self.log.wait_past(head, deadline - self.clock.monotonic())
            head = self.log.head()
            changes = self.log.pull_page(furthest, device.id)
            waiting = self.requests.waiting(device.id, query)
        if furthest < self.details.lowest_sequence():
            return PullAnswer((), self.log.head(), self.clock.time(), self.details.version(), True, waiting)
        return PullAnswer(tuple(changes), changes[-1].sequence if changes else head, self.clock.time(), self.details.version(), False, waiting)

    def trim(self) -> None:
        if self.clock.monotonic() - self.trimmed_at < TRIM_SECONDS:
            return
        self.trimmed_at = self.clock.monotonic()
        self.requests.lapse(self.clock.time())
        lowest = self.devices.lowest_pull()
        if lowest > self.details.lowest_sequence():
            self.log.trim(lowest)
            self.details.record_lowest_sequence(lowest)
