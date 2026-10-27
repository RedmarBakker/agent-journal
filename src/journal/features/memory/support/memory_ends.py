from datetime import datetime, timezone

from journal.repositories.memories import Memories
from journal.repositories.scope import Scope
from journal.support.actor import Actor


class MemoryEnds:
    """Removes the memories that end with a row closing or a moment passing, each as the system with its own removal event."""

    def __init__(self, memories: Memories, scope: Scope) -> None:
        self.memories, self.scope = memories, scope

    def row_closed(self, environment_id: int, row: str, time: float) -> None:
        with self.scope.environment(environment_id):
            for memory in self.memories.ending_with(row):
                self.memories.save(memory.removed(datetime.fromtimestamp(time, timezone.utc)), Actor.system())

    def moment_passed(self, environment_id: int, time: float) -> None:
        moment = datetime.fromtimestamp(time, timezone.utc)
        with self.scope.environment(environment_id):
            for memory in self.memories.expired(moment):
                self.memories.save(memory.removed(moment), Actor.system())
