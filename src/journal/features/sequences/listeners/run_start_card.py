from journal.chat.moment_cards import MomentCards
from journal.events.listener import Listener
from journal.events.rows.sequence_run_started import SequenceRunStarted
from journal.features.sequences.support.run_cards import RunCards
from journal.models.support.ref import Ref
from journal.support.card_type import CardType


class RunStartCard(Listener[SequenceRunStarted]):
    """A sequence started for an agent is shown as a card in the chat, the first of its run."""

    def __init__(self, runs: RunCards, cards: MomentCards) -> None:
        self.runs, self.cards = runs, cards

    def handle(self, event: SequenceRunStarted) -> None:
        run = event.run
        label = self.runs.recorded(event.environment_id, event.agent_session, run.sequence_id, run.title, "started")
        self.cards.show(event.environment_id, event.agent_session, label, row=Ref("sequences", run.sequence_id), shows=CardType.SEQUENCES, place=self.runs.place(run, 0))
