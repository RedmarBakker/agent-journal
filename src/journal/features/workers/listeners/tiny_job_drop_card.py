from journal.chat.moment_cards import MomentCards
from journal.events.listener import Listener
from journal.events.rows.tiny_job_dropped import TinyJobDropped
from journal.features.workers.support.dropped_score import DroppedScore
from journal.features.workers.support.fitness_band import FitnessBand
from journal.support.actor import Actor
from journal.support.card_kind import CardKind


class TinyJobDropCard(Listener[TinyJobDropped]):
    """A tiny job's drop in the fitness is a card in the chat, naming the score now, the points it cost and the cause."""

    def __init__(self, cards: MomentCards, scores: DroppedScore) -> None:
        self.cards, self.scores = cards, scores

    def handle(self, event: TinyJobDropped) -> None:
        score = self.scores.session_score(event.agent_session)
        label = f"Fitness fell {event.points} points to {score}"
        self.cards.show(event.environment_id, event.agent_session, label, detail=f"worker {event.worker} reported after {event.seconds} seconds with no other task open, a job to do yourself", actor=Actor.system(), shows=CardKind.FITNESS, outcome=FitnessBand.outcome(score))
