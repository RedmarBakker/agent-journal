from journal.chat.moment_cards import MomentCards
from journal.events.listener import Listener
from journal.events.rows.quick_report_dropped import QuickReportDropped
from journal.features.workers.support.dropped_score import DroppedScore
from journal.support.actor import Actor
from journal.support.card_kind import CardKind


class QuickReportDropCard(Listener[QuickReportDropped]):
    """A quick report's drop in the fitness is a card in the chat, naming the score now, the points it cost and the cause."""

    def __init__(self, cards: MomentCards, scores: DroppedScore) -> None:
        self.cards, self.scores = cards, scores

    def handle(self, event: QuickReportDropped) -> None:
        label = f"Fitness fell {event.points} points to {self.scores.session_score(event.agent_session)}"
        self.cards.show(event.environment_id, event.agent_session, label, detail=f"worker {event.worker} reported within minutes with {event.open_tasks} tasks open", actor=Actor.system(), shows=CardKind.FITNESS)
