from journal.events.models.created import Created
from journal.events.listener import Listener
from journal.features.sequences.support.announced_starts import AnnouncedStarts
from journal.models.scoped import Scoped
from journal.repositories.sequences import Sequences
from journal.support.agent_actor import AgentActor

class CreationStart(Listener[Created]):
    """A row an agent creates itself, never through a subagent it sent, starts the sequence that names that moment, such as Building a plan on plan.created: the run is stored on that agent, about that row; the first step is typed to the agent, and a worker, which cannot be typed to, is informed it at its next stop."""

    actors = (AgentActor,)

    def __init__(self, sequences: Sequences, starts: AnnouncedStarts) -> None:
        self.sequences, self.starts = sequences, starts

    def handle(self, event: Created) -> None:
        row = event.model
        if not isinstance(row, Scoped):
            return
        moment = f"{type(row).__name__.lower()}.created"
        for sequence in self.sequences.triggered_sequences(moment):
            self.starts.start(sequence, event.actor.id, row.environment_id, topic=f"{row.table()}:{row.id}")
            return
