import threading

from journal.repositories.outgoing_changes import OutgoingChanges
from journal.sync.block_supply import BlockSupply
from journal.sync.desk_answer import DeskAnswer
from journal.sync.incoming_changes import IncomingChanges
from journal.sync.journal_copy import JournalCopy
from journal.sync.rejected_edits import RejectedEdits
from journal.sync.sync_batch import SyncBatch
from journal.sync.team_account import TeamAccount
from journal.sync.team_change import TeamChange
from journal.sync.team_server_link import TeamServerLink
from journal.version import VERSION
from sync_server.full_copy import FullCopy
from sync_server.pool_slots import PoolSlots
from sync_server.pull_answer import PullAnswer
from sync_server.pull_query import PullQuery
from sync_server.sync_answer import SyncAnswer

BATCH_ROWS = 200


class TeamDesk:
    """The sync desk of a team this journal joined beside its home team, which the sync service's carrier for that team comes through: the pull's query by that team's sequence, the next batch of the changes queued for that team alone, a push's result and a pull's answer applied to that team's account, the team's own blocks of row numbers kept up, and its full copy laid in place of that team's rows alone; the home team's files, host requests, leases and upgrade are not that team's."""

    def __init__(self, account: TeamAccount, link: TeamServerLink, outgoing: OutgoingChanges, incoming: IncomingChanges, rejected: RejectedEdits, copy: JournalCopy, supply: BlockSupply) -> None:
        self.account, self.link, self.outgoing, self.incoming, self.rejected, self.copy, self.supply = account, link, outgoing, incoming, rejected, copy, supply
        self.applying = threading.Lock()

    def query(self, wait_seconds: float) -> PullQuery:
        return PullQuery(self.account.sequence(), wait_seconds, (), PoolSlots(0, 0), VERSION)

    def batch(self) -> SyncBatch:
        self.supply.refill()
        changes = self.outgoing.sending_batch(BATCH_ROWS, (self.account.key,))
        return SyncBatch(tuple(change.id for change in changes), (), False, TeamServerLink.push_body([change.payload() for change in changes], 0.0, self.query(0)))

    def batch_answered(self, ids: tuple[int, ...], answer: SyncAnswer) -> DeskAnswer:
        self.outgoing.sent(self.outgoing.sending_rows(list(ids)))
        self.rejected.apply(answer.settlement.rejected)
        return self.answered(answer.delivery)

    def answered(self, answer: PullAnswer) -> DeskAnswer:
        if answer.copy_needed and self.account.sequence() < answer.head:
            return DeskAnswer(0, True)
        with self.applying:
            sequence = self.account.sequence()
            changes = [TeamChange.logged(change) for change in answer.changes if change.sequence > sequence]
            self.incoming.apply(changes)
            self.account.record_pull(max(answer.head, sequence), answer.team_version)
            return DeskAnswer(len(changes), False)

    def copied(self, copy: FullCopy) -> bool:
        if copy.head <= self.account.sequence():
            return False
        with self.applying:
            self.copy.replace(copy.rows, self.outgoing.rows(), self.account)
            self.account.record_sequence(copy.head)
        return True
