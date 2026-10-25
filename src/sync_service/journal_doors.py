import json
import urllib.error
import urllib.request
from pathlib import Path

from sync_service.desk_answer import DeskAnswer
from sync_service.desk_batch import DeskBatch
from sync_service.desk_query import DeskQuery
from sync_service.journal_busy import JournalBusy
from sync_service.journal_mismatch import JournalMismatch
from sync_service.team_address import TeamAddress

SECRET_HEADER = "x-journal-sync-secret"
PROTOCOL_HEADER = "x-journal-desk-protocol"
# the version of the sync doors this service speaks, which the journal server answers only when it is its own
DESK_PROTOCOL = 3
CALL_SECONDS = 30
COPY_SECONDS = 300
SYNC_PATH = "/journal/sync"


class JournalDoors:
    """The journal server's doors as the sync service reaches them, the home team's or, bound to its key, a further team's: each call reads the server's port and its service secret anew from the journal's folder, since a server started again takes a new port and a new secret, and a server that is down, starting or on a new secret answers JournalBusy; the team's answers are handed in as the bytes the team sent."""

    def __init__(self, root: Path, team: str = "") -> None:
        self.port_file, self.secret_file = root / ".journal" / "port", root / ".journal" / "runtime" / "sync-secret"
        self.team_key = team

    def bound(self, team: str) -> "JournalDoors":
        return JournalDoors(self.port_file.parent.parent, team)

    def teams(self) -> list[str]:
        return list(json.loads(self.called("GET", f"{SYNC_PATH}/teams", None, CALL_SECONDS)).get("keys", []))

    def secret(self) -> str:
        return self.secret_file.read_text() if self.secret_file.is_file() else ""

    def register(self, name: str, address: str, events: tuple[str, ...]) -> None:
        self.called("POST", "/journal/services", self.encoded({"name": name, "address": address, "events": list(events)}), CALL_SECONDS)

    def team(self) -> TeamAddress:
        return TeamAddress.parsed(**json.loads(self.called("GET", f"{SYNC_PATH}/team", None, CALL_SECONDS)))

    def state(self, fault: str, reached: bool) -> None:
        self.called("POST", f"{SYNC_PATH}/state", self.encoded({"fault": fault, "reached": reached}), CALL_SECONDS)

    def query(self, wait_seconds: float) -> DeskQuery:
        query = json.loads(self.called("GET", f"{SYNC_PATH}/query?wait_seconds={wait_seconds}", None, CALL_SECONDS))
        return DeskQuery(query["path"], query["wait_seconds"])

    def batch(self) -> DeskBatch:
        return DeskBatch.parsed(**json.loads(self.called("GET", f"{SYNC_PATH}/batch", None, CALL_SECONDS)))

    def files_sent(self, ids: tuple[int, ...]) -> None:
        self.called("POST", f"{SYNC_PATH}/files-sent", self.encoded({"ids": list(ids)}), CALL_SECONDS)

    # the team server's answer to a push, handed in for the batch it names
    def batch_answer(self, ids: tuple[int, ...], answer: bytes) -> DeskAnswer:
        return DeskAnswer(**json.loads(self.called("POST", f"{SYNC_PATH}/pushed?ids={','.join(map(str, ids))}", answer, CALL_SECONDS)))

    # the pull a push's answer carried, handed in again once the team's full copy is laid in
    def batch_delivery(self, answer: bytes) -> DeskAnswer:
        return DeskAnswer(**json.loads(self.called("POST", f"{SYNC_PATH}/delivery", answer, CALL_SECONDS)))

    def team_answer(self, answer: bytes) -> DeskAnswer:
        return DeskAnswer(**json.loads(self.called("POST", f"{SYNC_PATH}/answer", answer, CALL_SECONDS)))

    def install_copy(self, copy: bytes) -> None:
        self.called("POST", f"{SYNC_PATH}/copy", copy, COPY_SECONDS)

    def upgrade_claimed(self) -> None:
        self.called("POST", f"{SYNC_PATH}/upgrade-claimed", b"{}", CALL_SECONDS)

    def upgrade_finished(self) -> None:
        self.called("POST", f"{SYNC_PATH}/upgrade-finished", b"{}", CALL_SECONDS)

    @staticmethod
    def encoded(fields: dict) -> bytes:
        return json.dumps(fields).encode()

    def called(self, method: str, path: str, body: bytes | None, seconds: float) -> bytes:
        port, secret = self.port_file.read_text().strip() if self.port_file.is_file() else "", self.secret()
        if not port.isdigit() or not secret:
            raise JournalBusy("the journal server is not running")
        path = f"{path}{'&' if '?' in path else '?'}team={self.team_key}" if self.team_key else path
        request = urllib.request.Request(f"http://127.0.0.1:{port}{path}", data=body, method=method, headers={"Content-Type": "application/json", SECRET_HEADER: secret, PROTOCOL_HEADER: str(DESK_PROTOCOL)})
        try:
            with urllib.request.urlopen(request, timeout=seconds) as answer:
                return answer.read() or b"{}"
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
