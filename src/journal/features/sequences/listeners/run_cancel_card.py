from journal.chat.moment_cards import MomentCards
from journal.events.listener import Listener
from journal.events.rows.sequence_run_cancelled import SequenceRunCancelled
from journal.features.sequences.support.run_cards import RunCards
from journal.models.support.ref import Ref
from journal.support.card_kind import CardKind


class RunCancelCard(Listener[SequenceRunCancelled]):
    """A sequence the user ended is shown as a card with the step it ended at."""

    def __init__(self, runs: RunCards, cards: MomentCards) -> None:
        self.runs, self.cards = runs, cards

    def handle(self, event: SequenceRunCancelled) -> None:
        run = event.run
        self.cards.show(event.environment_id, event.agent_session, self.runs.recorded(event.environment_id, event.agent_session, run.sequence_id, run.title, f"ended at step {run.step + 1}"), row=Ref("sequences", run.sequence_id), shows=CardKind.SEQUENCES)
