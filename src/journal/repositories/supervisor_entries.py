from journal.models.entry import Entry
from journal.repositories.entries import Entries
from journal.support.actor import Actor


class SupervisorEntries:
    """The checked writer for protected supervisor entries, sharing Entry's idempotency origin."""

    def __init__(self, entries: Entries) -> None:
        self.entries = entries

    def recorded(self, entry: Entry, actor: Actor) -> Entry:
        return self.entries.recorded_control(entry, actor)

    def erase_expired_observations(self, now_ms: int) -> None:
        self.entries._erase_expired_supervisor_observations(now_ms)
