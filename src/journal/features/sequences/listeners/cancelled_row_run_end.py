from journal.events.models.updated import Updated
from journal.events.listener import Listener
from journal.features.sequences.support.run_tracker import RunTracker
from journal.models.scoped import Scoped

CANCELLED = "cancelled"


class CancelledRowRunEnd(Listener[Updated]):
    """A row a run is about that is cancelled ends the run, which its sequence state answers, telling the agent."""

    def __init__(self, active: RunTracker) -> None:
        self.running = active

    def handle(self, event: Updated) -> None:
        row = event.model
        if not isinstance(row, Scoped) or "state" not in event.changed() or getattr(row, "state", "") != CANCELLED:
            return
        ref = f"{row.table()}:{row.id}"
        self.running.finish_matching(row.environment_id, lambda run: run.subject == ref, f"{ref} was cancelled")
