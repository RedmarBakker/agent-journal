from journal.chat.moment_cards import MomentCards
from journal.events.listener import Listener
from journal.events.rows.sequence_step_moved import SequenceStepMoved
from journal.features.sequences.support.run_cards import RunCards
from journal.models.support.ref import Ref
from journal.support.card_type import CardType


class RunStepCard(Listener[SequenceStepMoved]):
    """A step finished by the agent or skipped by the user is shown as a card: the next step it moves on to among the steps, or the sequence finished among the sequences."""

    def __init__(self, runs: RunCards, cards: MomentCards) -> None:
        self.runs, self.cards = runs, cards

    def handle(self, event: SequenceStepMoved) -> None:
        run = event.run
        label = self.runs.step_moved(event.environment_id, event.agent_session, run)
        shows = CardType.SEQUENCES if run.last else CardType.SEQUENCE_STEPS
        self.cards.show(event.environment_id, event.agent_session, label, row=Ref("sequences", run.sequence_id), shows=shows, place=self.runs.place(run, run.step + 1))
