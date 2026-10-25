from dataclasses import dataclass

from journal.features.reviewing.support.point_verdict import PointVerdict

GOOD, BAD = "good", "bad"
TONES = {PointVerdict.PASSED: GOOD, PointVerdict.SHORT: BAD, PointVerdict.UNDECIDED: ""}


@dataclass(frozen=True)
class ReviewPoint:
    """One point of a reviewer's report: its number, whether it passed, fell short or could not be decided, and why."""

    number: int
    verdict: PointVerdict
    reason: str = ""

    def line(self) -> str:
        return f"Point {self.number} {self.verdict}: {self.reason}".rstrip(": ")

    def tone(self) -> str:
        return TONES[self.verdict]
