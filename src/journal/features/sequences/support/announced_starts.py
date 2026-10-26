from journal.features.sequences.support.run_tracker import RunTracker
from journal.models.sequence import Sequence
from journal.supervisor_link import SupervisorLink


class AnnouncedStarts:
    """A sequence started by its trigger rather than by the agent's command, its first step typed to the agent when it runs in a terminal the journal types into."""

    def __init__(self, runs: RunTracker, supervisor: SupervisorLink) -> None:
        self.runs, self.supervisor = runs, supervisor

    def start(self, sequence: Sequence, session: str, environment_id: int, topic: str = "") -> None:
        line = self.runs.start(sequence, session, environment_id, topic)
        if line and self.runs.typed_agent(session, environment_id):
            self.supervisor.type(environment_id, line)
