from journal.events.models.deleted import Deleted
from journal.events.listener import Listener
from journal.features.sequences.support.run_tracker import RunTracker


class RunTermination(Listener[Deleted]):
    """What a listener that ends runs at a deletion shares: the runs it names cannot finish, which their sequence states answer, telling the agent."""

    def __init__(self, active: RunTracker) -> None:
        self.running = active

    def notice(self, environment_id: int, missing, reason: str) -> None:
        self.running.finish_matching(environment_id, missing, reason)
