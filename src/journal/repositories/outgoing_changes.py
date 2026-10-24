from journal.models.outgoing_change import OutgoingChange
from journal.repositories.repository import Repository
from journal.support.actor import Actor


class OutgoingChanges(Repository[OutgoingChange]):
    """The writes waiting for the team server, oldest first; a write to a row whose change still waits is folded into it, never into one being sent; folding, dropping and taking a batch to send each happen in one transaction, since the hooks fold changes while the sync thread takes them."""

    model = OutgoingChange

    def queued(self, change: OutgoingChange, actor: Actor) -> None:
        with self.connection.transaction():
            self.folded(change, actor)

    def folded(self, change: OutgoingChange, actor: Actor) -> None:
        waiting = self.all_matching(row_table=change.row_table, row=change.row, is_sending=False)
        if not waiting:
            self.save(change, actor)
            return
        merged = waiting[0].merged(change)
        if merged is None:
            self.delete(waiting[0], actor)
        else:
            self.save(merged, actor)

    def queued_fields(self, table: str, row: int) -> set[str]:
        return {name for change in self.all_matching(row_table=table, row=row) for name in change.fields or {}}

    def dropped(self, table: str, row: int, actor: Actor) -> None:
        with self.connection.transaction():
            for change in self.all_matching(row_table=table, row=row, is_sending=False):
                self.delete(change, actor)

    def waiting(self) -> list[OutgoingChange]:
        return self.all_matching(is_sending=False)

    def sending_batch(self, limit: int) -> list[OutgoingChange]:
        with self.connection.transaction():
            outstanding = self.all_matching(is_sending=True)
            if outstanding:
                return outstanding[:limit]
            for change in self.waiting()[:limit]:
                self.save(change.with_(is_sending=True), Actor.system())
        return self.all_matching(is_sending=True)[:limit]

    def sending_rows(self, ids: list[int]) -> list[OutgoingChange]:
        return [change for change in self.all_matching(is_sending=True) if change.id in set(ids)]

    def sent(self, changes: list[OutgoingChange]) -> None:
        for change in changes:
            self.delete(change, Actor.system())

    def commit_callback(self, work) -> None:
        self.connection.commit_callback(work)

    def clear(self) -> None:
        self._purged(self.query())
