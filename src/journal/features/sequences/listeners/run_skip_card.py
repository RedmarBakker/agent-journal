from journal.chat.moment_cards import MomentCards
from journal.events.listener import Listener
from journal.events.rows.sequence_step_skipped import SequenceStepSkipped
from journal.features.sequences.support.run_cards import RunCards
from journal.models.support.ref import Ref
from journal.support.card_type import CardType


class RunSkipCard(Listener[SequenceStepSkipped]):
    """A step the user skipped is shown as a card, as a finished step is: the next step among the steps, or the sequence finished among the sequences."""

    def __init__(self, runs: RunCards, cards: MomentCards) -> None:
        self.runs, self.cards = runs, cards

    def handle(self, event: SequenceStepSkipped) -> None:
        run = event.run
        self.cards.show(event.environment_id, event.agent_session, self.runs.step_moved(event.environment_id, event.agent_session, run), row=Ref("sequences", run.sequence_id), shows=CardType.SEQUENCES if run.last else CardType.SEQUENCE_STEPS)
