from journal.events.listener import Listener
from journal.events.rows.sequence_step_skipped import SequenceStepSkipped
from journal.features.sequences.support.run_cards import RunCards


class RunSkipCard(Listener[SequenceStepSkipped]):
    """A step the user skipped is shown as a card, as a finished step is: the next step among the steps, or the sequence finished among the sequences."""

    def __init__(self, runs: RunCards) -> None:
        self.runs = runs

    def handle(self, event: SequenceStepSkipped) -> None:
        self.runs.step_moved(event.environment_id, event.agent_session, event.run)
