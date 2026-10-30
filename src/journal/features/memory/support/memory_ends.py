from datetime import datetime, timezone

from journal.features.memory.support.closed_rows import ClosedRows
from journal.models.support.ref import Ref
from journal.repositories.memories import Memories
from journal.repositories.scope import Scope
from journal.support.actor import Actor


class MemoryEnds:
    """Removes the memories that end with a moment passing, and at a compaction those tied to a task or plan that is closed, each as the system with its own removal event."""

    def __init__(self, memories: Memories, scope: Scope, closed_rows: ClosedRows) -> None:
        self.memories, self.scope, self.closed_rows = memories, scope, closed_rows

    def tied_closed(self, owner: Ref | None, time: float) -> None:
        for memory in self.memories.tied(owner):
            if self.closed_rows.closed_state(Ref.parse(memory.expiry_row)):
                self.memories.save(memory.removed(datetime.fromtimestamp(time, timezone.utc)), Actor.system())

    def moment_passed(self, environment_id: int, time: float) -> None:
        moment = datetime.fromtimestamp(time, timezone.utc)
        with self.scope.environment(environment_id):
            for memory in self.memories.expired(moment):
                self.memories.save(memory.removed(moment), Actor.system())
