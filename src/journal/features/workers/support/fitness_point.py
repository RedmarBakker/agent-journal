from dataclasses import dataclass
from typing import ClassVar

from journal.features.workers.support.fitness_score import FitnessScore
from journal.models.agent import Agent
from journal.models.entry import Entry
from journal.support.actor import Actor


@dataclass(frozen=True)
class FitnessPoint:
    """One fitness score of an agent as the journal computed it, kept as an entry of kind fitness: when, in which mode, the score, whether it was measured, the measures off the ideal, how close each scored measure came in percent, and what moved it from the point before."""

    KIND: ClassVar[str] = "fitness"

    at: float
    mode: str
    score: int
    is_measured: bool
    gaps: tuple[str, ...]
    parts: tuple[tuple[str, int], ...]
    moved: str

    @classmethod
    def first(cls, score: FitnessScore, at: float) -> "FitnessPoint":
        return cls.of(score, at, "first score in this mode" if score.is_measured else "not scored yet: too few tool uses in this mode")

    @classmethod
    def of(cls, score: FitnessScore, at: float, moved: str) -> "FitnessPoint":
        return cls(at, score.mode, score.score, score.is_measured, score.lines, score.parts, moved)

    @classmethod
    def parsed(cls, data: dict) -> "FitnessPoint":
        return cls(float(data["at"]), data["mode"], int(data["score"]), bool(data["is_measured"]), tuple(data["gaps"]), tuple((label, int(percent)) for label, percent in data["parts"]), data["moved"])

    def is_same(self, score: FitnessScore) -> bool:
        return (self.mode, self.score, self.is_measured, self.gaps, self.parts) == (score.mode, score.score, score.is_measured, score.lines, score.parts)

    def following(self, score: FitnessScore, at: float) -> "FitnessPoint":
        if score.mode != self.mode or not score.is_measured or not self.is_measured:
            return FitnessPoint.first(score, at)
        return FitnessPoint.of(score, at, self.change(dict(score.parts)))

    def change(self, after: dict[str, int]) -> str:
        before = dict(self.parts)
        moves = [*((abs(after[label] - before[label]), f"{label}: {before[label]}% to {after[label]}% of the ideal") for label in after if label in before),
                 *((100 - after[label], f"{label}: scored from now, {after[label]}% of the ideal") for label in after if label not in before),
                 *((100 - before[label], f"{label}: left out, too few events") for label in before if label not in after)]
        return max(moves, key=lambda move: move[0])[1] if moves else "the measures off the ideal changed"

    def entry(self, agent: Agent) -> Entry:
        data = {"session": agent.session, "at": self.at, "mode": self.mode, "score": self.score, "is_measured": self.is_measured, "gaps": list(self.gaps), "parts": [list(part) for part in self.parts], "moved": self.moved}
        return Entry(environment_id=agent.environment_id, kind=FitnessPoint.KIND, actor=Actor.system(), data=data)

    def shown(self) -> dict:
        return {"at": self.at, "score": self.score, "is_measured": self.is_measured, "gaps": list(self.gaps), "moved": self.moved}
