import json
import urllib.error
import urllib.request
from dataclasses import asdict

from journal.config import Config
from journal.sync.desk_answer import DeskAnswer
from journal.sync.desk_busy import DeskBusy
from journal.sync.sync_batch import SyncBatch
from journal.sync.sync_secret import SECRET_FILE, SECRET_HEADER
from journal.sync.waiting_file import WaitingFile
from sync_server.file_place import FilePlace
from sync_server.full_copy import FullCopy
from sync_server.pool_slots import PoolSlots
from sync_server.pull_answer import PullAnswer
from sync_server.pull_query import PullQuery
from sync_server.sync_answer import SyncAnswer

CALL_SECONDS = 30
COPY_SECONDS = 300
SYNC_PATH = "/journal/sync"


class LocalDoors:
    """The sync desk reached over the journal server's local doors, from a carrier in a process of its own: each call reads the port file and the sync secret anew, since a journal can move port and takes a new secret when it starts again, and a server that is down or starting answers DeskBusy."""

    def __init__(self, config: Config) -> None:
        self.config = config

    def query(self, wait_seconds: float) -> PullQuery:
        answer = self.called("GET", f"/query?wait_seconds={wait_seconds}", None, CALL_SECONDS)
        return PullQuery(answer["sequence"], answer["wait_seconds"], tuple(answer["environment_keys"]), PoolSlots(**answer["pool"]), answer["version"])

    def batch(self, wait_seconds: float) -> SyncBatch:
        answer = self.called("GET", f"/batch?wait_seconds={wait_seconds}", None, wait_seconds + CALL_SECONDS)
        files = tuple(WaitingFile(file["id"], FilePlace(**file["place"]), file["path"]) for file in answer["files"])
        return SyncBatch(tuple(answer["ids"]), tuple(answer["changes"]), files, answer["upgrader"])

    def files_sent(self, ids: tuple[int, ...]) -> None:
        self.called("POST", "/files-sent", {"ids": list(ids)}, CALL_SECONDS)

    def pushed(self, batch: SyncBatch, answer: SyncAnswer) -> DeskAnswer:
        return DeskAnswer(**self.called("POST", "/pushed", {"ids": list(batch.ids), "answer": {"settlement": asdict(answer.settlement), "delivery": asdict(answer.delivery)}}, CALL_SECONDS))

    def answered(self, answer: PullAnswer) -> DeskAnswer:
        return DeskAnswer(**self.called("POST", "/answer", asdict(answer), CALL_SECONDS))

    def copied(self, copy: FullCopy) -> bool:
        return self.called("POST", "/copy", asdict(copy), COPY_SECONDS)["laid_in"]

    def upgrade_claimed(self) -> None:
        self.called("POST", "/upgrade-claimed", {}, CALL_SECONDS)

    def upgrade_finished(self) -> None:
        self.called("POST", "/upgrade-finished", {}, CALL_SECONDS)

    def wake(self) -> None:
        return None

    def called(self, method: str, path: str, body: dict | None, seconds: float) -> dict:
        port, secret = self.config.stored_port(), self.config.home / "runtime" / SECRET_FILE
        if not port or not secret.is_file():
            raise DeskBusy("the journal server is not running")
        request = urllib.request.Request(f"http://127.0.0.1:{port[0]}{SYNC_PATH}{path}", data=None if body is None else json.dumps(body).encode(), method=method, headers={"Content-Type": "application/json", SECRET_HEADER: secret.read_text()})
        try:
            with urllib.request.urlopen(request, timeout=seconds) as answer:
                return json.loads(answer.read())
        except urllib.error.HTTPError as refusal:
            if refusal.code == 503:
                raise DeskBusy("the journal server is starting") from refusal
            raise
        except (ConnectionRefusedError, urllib.error.URLError) as down:
            raise DeskBusy(f"the journal server did not answer: {down}") from down
