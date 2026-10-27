from journal.events.listener import Listener
from journal.events.rows.sequence_step_finished import SequenceStepFinished
from journal.features.sequences.support.run_cards import RunCards


class RunStepCard(Listener[SequenceStepFinished]):
    """A finished step is shown as a card: the next step it moves on to among the steps, or the sequence finished among the sequences."""

    def __init__(self, runs: RunCards) -> None:
        self.runs = runs

    def handle(self, event: SequenceStepFinished) -> None:
        self.runs.step_moved(event.environment_id, event.agent_session, event.run)
