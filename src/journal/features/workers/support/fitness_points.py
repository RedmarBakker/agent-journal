from journal.features.workers.support.fitness_point import FitnessPoint
from journal.features.workers.support.fitness_scoring import FitnessScoring
from journal.models.agent import Agent
from journal.repositories.entries import Entries
from journal.support.actor import Actor


class FitnessPoints:
    """An agent's fitness scored as the status bar shows it and kept as a point of its timeline whenever the score itself moves, or the mode, whether it is measured, or a drop, never for a measure that moves under an unchanged score: after its own tool uses and after each report its workers file."""

    def __init__(self, scoring: FitnessScoring, entries: Entries) -> None:
        self.scoring, self.entries = scoring, entries

    def recorded(self, agent: Agent, time: float) -> None:
        score = self.scoring.scored(agent)
        if score is None:
            return
        newest = self.entries.session_kind_newest(agent.session, FitnessPoint.KIND, 1)
        if not newest:
            self.entries.save(FitnessPoint.first(score, time).entry(agent), Actor.system())
            return
        last_point = FitnessPoint.parsed(newest[0].data)
        if not last_point.is_same(score):
            self.entries.save(last_point.following(score, time).entry(agent), Actor.system())
