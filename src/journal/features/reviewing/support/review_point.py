from journal.support.card_outcome import CardOutcome
from dataclasses import dataclass

from journal.features.reviewing.support.point_verdict import PointVerdict

OUTCOMES = {PointVerdict.PASSED: CardOutcome.PASSED, PointVerdict.SHORT: CardOutcome.FAILED, PointVerdict.UNDECIDED: CardOutcome.NONE}


@dataclass(frozen=True)
class ReviewPoint:
    """One point of a reviewer's report: its number, whether it passed, fell short or could not be decided, and why."""

    number: int
    verdict: PointVerdict
    reason: str = ""

    def line(self) -> str:
        return f"Point {self.number} {self.verdict}: {self.reason}".rstrip(": ")

    def outcome(self) -> CardOutcome:
        return OUTCOMES[self.verdict]
