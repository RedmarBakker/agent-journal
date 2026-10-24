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
    """The sync desk as its doors offer it to the sync service: the query a pull asks with, the queue's next batch with the files waiting and the push the team takes them in, each answer the team gave taken back, and the team's full copy laid in."""

    def __init__(self, desk: SyncDesk) -> None:
        self.desk = desk

    def query(self, wait_seconds: float) -> PullQuery:
        return self.desk.query(wait_seconds)

    def batch(self) -> SyncBatch:
        self.desk.kept_up()
        with self.desk.held(self.desk.sending, "take a batch"):
            changes = self.desk.batch(BATCH_ROWS)
        files = tuple(WaitingFile(upload.id, place, str(path), place.address()) for upload in self.desk.waiting_files() for place, path in [self.desk.file_place(upload)])
        return SyncBatch(tuple(change.id for change in changes), files, self.desk.is_upgrader(), self.desk.push_body(changes))

    def files_sent(self, ids: tuple[int, ...]) -> None:
        self.desk.files_sent(list(ids))

    def pushed(self, ids: tuple[int, ...], answer: SyncAnswer) -> DeskAnswer:
        return self.desk.push_taken(list(ids), answer)

    def answered(self, answer: PullAnswer) -> DeskAnswer:
        return self.desk.taken(answer)

    def copied(self, copy: FullCopy) -> bool:
        return self.desk.copy_laid_in(copy)

    def upgrade_claimed(self) -> None:
        self.desk.upgrade_claimed()

    def upgrade_finished(self) -> None:
        self.desk.upgrade_finished()
