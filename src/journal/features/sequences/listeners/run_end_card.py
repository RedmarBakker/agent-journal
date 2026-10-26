from journal.chat.moment_cards import MomentCards
from journal.events.listener import Listener
from journal.models.support.ref import Ref
from journal.events.rows.sequence_run_cannot_finish import SequenceRunCannotFinish
from journal.features.sequences.support.run_cards import RunCards
from journal.repositories.sequences import Sequences
from journal.support.card_type import CardType


class RunEndCard(Listener[SequenceRunCannotFinish]):
    """A sequence that cannot finish, since what it was about is gone, is shown as a card with why."""

    def __init__(self, runs: RunCards, cards: MomentCards, sequences: Sequences) -> None:
        self.runs, self.cards, self.sequences = runs, cards, sequences

    def handle(self, event: SequenceRunCannotFinish) -> None:
        titles = [sequence.title for sequence in self.sequences.matching(id=event.sequence_id)]
        self.cards.show(event.environment_id, event.agent_session, self.runs.recorded(event.environment_id, event.agent_session, event.sequence_id, titles[0] if titles else f"sequence {event.sequence_id}", f"ended: {event.reason}"), row=Ref("sequences", event.sequence_id), shows=CardType.SEQUENCES)
