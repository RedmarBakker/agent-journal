import json
import sys
import urllib.error
import urllib.request
import uuid
from datetime import datetime, timezone

from journal.engine.job import Job
from journal.features.faults.faults_options import FaultsOptions
from journal.features.faults.support.sentry_address import SentryAddress
from journal.repositories.setting_rows import SettingRows
from journal.support.fault_log import FaultLog
from journal.support.recorded_fault import RecordedFault
from journal.support.rejection import Rejection
from journal.version import VERSION

SENTRY_TIMEOUT_SECONDS = 5


class SentrySender(Job):
    """Every ten seconds the faults the fault log gathered since are sent, one event each, to the Sentry project the setting names, from this job's own thread so no request waits on it; with no project named they are dropped unsent, so nothing builds up to leave later."""

    interval_seconds = 10.0

    def __init__(self, faults: FaultLog, settings: SettingRows) -> None:
        self.faults, self.settings = faults, settings

    def tick(self, time: float) -> None:
        faults = self.faults.drained()
        dsn = str(self.settings.option(FaultsOptions.SENTRY_DSN)).strip()
        if not dsn or not faults:
            return
        try:
            address = SentryAddress.parsed(dsn)
        except Rejection as wrong:
            sys.stderr.write(f"faults are not sent: {wrong}\n")
            return
        for fault in faults:
            self.sent(address, fault)

    def sent(self, address: SentryAddress, fault: RecordedFault) -> None:
        event_id = uuid.uuid4().hex
        event = {
            "event_id": event_id, "timestamp": datetime.fromtimestamp(fault.time, timezone.utc).isoformat(), "platform": "python", "level": "error",
            "release": f"agent-journal@{fault.version}", "tags": {"place": fault.place},
            "exception": {"values": [{"type": fault.fault_type, "value": fault.text, "stacktrace": {"frames": list(fault.frames)}}]},
        }
        body = "\n".join(json.dumps(part) for part in ({"event_id": event_id, "dsn": address.dsn}, {"type": "event"}, event)).encode()
        auth = f"Sentry sentry_version=7, sentry_key={address.public_key}, sentry_client=agent-journal/{VERSION}"
        request = urllib.request.Request(address.envelope_url, data=body, headers={"Content-Type": "application/x-sentry-envelope", "X-Sentry-Auth": auth}, method="POST")
        try:
            with urllib.request.urlopen(request, timeout=SENTRY_TIMEOUT_SECONDS):
                return
        except (urllib.error.URLError, TimeoutError) as unsent:
            self.faults.unsent(fault, unsent)
