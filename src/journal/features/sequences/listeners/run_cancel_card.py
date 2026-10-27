from journal.events.listener import Listener
from journal.events.rows.sequence_run_cancelled import SequenceRunCancelled
from journal.features.sequences.support.run_cards import RunCards
from journal.support.card_type import CardType


class RunCancelCard(Listener[SequenceRunCancelled]):
    """A sequence the user ended is shown as a card with the step it ended at."""

    def __init__(self, runs: RunCards) -> None:
        self.runs = runs

    def handle(self, event: SequenceRunCancelled) -> None:
        run = event.run
        self.runs.shown(event.environment_id, event.agent_session, run, f"ended at step {run.step + 1}", run.step + 1, CardType.SEQUENCES)
