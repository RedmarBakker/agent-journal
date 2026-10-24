import json
import urllib.error
import urllib.request
from pathlib import Path

from sync_service.journal_busy import JournalBusy
from sync_service.journal_mismatch import JournalMismatch

SECRET_HEADER = "x-journal-sync-secret"
PROTOCOL_HEADER = "x-journal-desk-protocol"
# the version of the sync doors this service speaks, which the journal server answers only when it is its own
DESK_PROTOCOL = 2
CALL_SECONDS = 30
COPY_SECONDS = 300
SYNC_PATH = "/journal/sync"


class JournalDoors:
    """The journal server's doors as the sync service reaches them: each call reads the server's port and its service secret anew from the journal's folder, since a server started again takes a new port and a new secret, and a server that is down, starting or on a new secret answers JournalBusy."""

    def __init__(self, root: Path) -> None:
        self.port_file, self.secret_file = root / ".journal" / "port", root / ".journal" / "runtime" / "sync-secret"

    def secret(self) -> str:
        return self.secret_file.read_text() if self.secret_file.is_file() else ""

    def register(self, name: str, address: str, events: tuple[str, ...]) -> None:
        self.called("POST", "/journal/services", {"name": name, "address": address, "events": list(events)}, CALL_SECONDS)

    def team(self) -> dict:
        return self.called("GET", f"{SYNC_PATH}/team", None, CALL_SECONDS)

    def state(self, fault: str, reached: bool) -> None:
        self.called("POST", f"{SYNC_PATH}/state", {"fault": fault, "reached": reached}, CALL_SECONDS)

    def query(self, wait_seconds: float) -> dict:
        return self.called("GET", f"{SYNC_PATH}/query?wait_seconds={wait_seconds}", None, CALL_SECONDS)

    def batch(self) -> dict:
        return self.called("GET", f"{SYNC_PATH}/batch?wait_seconds=0", None, CALL_SECONDS)

    def files_sent(self, ids: list[int]) -> None:
        self.called("POST", f"{SYNC_PATH}/files-sent", {"ids": ids}, CALL_SECONDS)

    def pushed(self, ids: list[int], answer: dict) -> dict:
        return self.called("POST", f"{SYNC_PATH}/pushed", {"ids": ids, "answer": answer}, CALL_SECONDS)

    def answered(self, answer: dict) -> dict:
        return self.called("POST", f"{SYNC_PATH}/answer", answer, CALL_SECONDS)

    def copied(self, copy: dict) -> bool:
        return self.called("POST", f"{SYNC_PATH}/copy", copy, COPY_SECONDS)["laid_in"]

    def upgrade_claimed(self) -> None:
        self.called("POST", f"{SYNC_PATH}/upgrade-claimed", {}, CALL_SECONDS)

    def upgrade_finished(self) -> None:
        self.called("POST", f"{SYNC_PATH}/upgrade-finished", {}, CALL_SECONDS)

    def called(self, method: str, path: str, body: dict | None, seconds: float) -> dict:
        port, secret = self.port_file.read_text().strip() if self.port_file.is_file() else "", self.secret()
        if not port.isdigit() or not secret:
            raise JournalBusy("the journal server is not running")
        request = urllib.request.Request(f"http://127.0.0.1:{port}{path}", data=None if body is None else json.dumps(body).encode(), method=method, headers={"Content-Type": "application/json", SECRET_HEADER: secret, PROTOCOL_HEADER: str(DESK_PROTOCOL)})
        try:
            with urllib.request.urlopen(request, timeout=seconds) as answer:
                return json.loads(answer.read() or b"{}")
        except urllib.error.HTTPError as refusal:
            raise self.refused(refusal) from refusal
        except (ConnectionError, urllib.error.URLError) as down:
            raise JournalBusy(f"the journal server did not answer: {down}") from down

    @staticmethod
    def refused(refusal: urllib.error.HTTPError) -> Exception:
        if refusal.code == 503:
            return JournalBusy("the journal server is starting")
        if refusal.code == 403:
            return JournalBusy("the journal server started again with a new secret")
        if refusal.code == 426:
            return JournalMismatch(json.loads(refusal.read() or b"{}").get("error", "the journal server speaks another version of the sync doors"))
        if refusal.code == 404:
            return JournalMismatch("the journal server has no sync doors of this version: restart the journal so both run the same code")
        return OSError(f"the journal server answered {refusal.code}: {json.loads(refusal.read() or b'{}').get('error', refusal.reason)}")
