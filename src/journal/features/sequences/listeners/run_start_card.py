from journal.events.listener import Listener
from journal.events.rows.sequence_run_started import SequenceRunStarted
from journal.features.sequences.support.run_cards import RunCards
from journal.support.card_type import CardType


class RunStartCard(Listener[SequenceRunStarted]):
    """A sequence started for an agent is shown as a card in the chat."""

    def __init__(self, runs: RunCards) -> None:
        self.runs = runs

    def handle(self, event: SequenceRunStarted) -> None:
        self.runs.shown(event.environment_id, event.agent_session, event.run, "started", 0, CardType.SEQUENCES)
