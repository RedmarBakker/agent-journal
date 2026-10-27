from journal.sync.desk_answer import DeskAnswer
from journal.sync.sync_batch import SyncBatch
from journal.sync.sync_desk import SyncDesk
from journal.sync.waiting_file import WaitingFile
from sync_server.full_copy import FullCopy
from sync_server.pull_answer import PullAnswer
from sync_server.pull_query import PullQuery
from sync_server.sync_answer import SyncAnswer

BATCH_ROWS = 200


class ServerDoors:
    """The sync desk as its doors offer it to the sync service: the query a pull asks with, the queue's next batch with the files waiting and the push the team takes them in, each answer the team gave taken back, and the team's full copy laid in. A push's pull is handed again once the team's full copy is laid in."""

    def __init__(self, desk: SyncDesk) -> None:
        self.desk = desk

    def query(self, wait_seconds: float) -> PullQuery:
        return self.desk.query(wait_seconds)

    def batch(self) -> SyncBatch:
        self.desk.refresh()
        with self.desk.locked(self.desk.sending, "take a batch"):
            changes = self.desk.batch(BATCH_ROWS)
        files = tuple(WaitingFile(upload.id, place, str(path), place.address()) for upload in self.desk.waiting_files() for place, path in [self.desk.file_place(upload)])
        return SyncBatch(tuple(change.id for change in changes), files, self.desk.is_upgrader(), self.desk.request_body(changes))

    def files_sent(self, ids: tuple[int, ...]) -> None:
        self.desk.files_sent(list(ids))

    def batch_answered(self, ids: tuple[int, ...], answer: SyncAnswer) -> DeskAnswer:
        return self.desk.outgoing_reply(list(ids), answer)

    def delivered(self, answer: SyncAnswer) -> DeskAnswer:
        return self.desk.delivery_reply(answer.delivery)

    def answered(self, answer: PullAnswer) -> DeskAnswer:
        return self.desk.delivery_reply(answer)

    def copied(self, copy: FullCopy) -> bool:
        return self.desk.apply_copy(copy)

    def upgrade_claimed(self) -> None:
        self.desk.upgrade_claimed()

    def upgrade_finished(self) -> None:
        self.desk.upgrade_finished()
