import re
from dataclasses import dataclass

from journal.features.reviewing.support.point_verdict import PointVerdict
from journal.features.reviewing.support.review_point import ReviewPoint

# a report's lines, one per point and one for the tests, written on lines of their own or as sentences one after another
LINE_BREAK = re.compile(r"\n|(?<=\.)\s+(?=\d+\s*[.:)]?\s+(?:passed|short|undecided)\b|tests?\b)", re.IGNORECASE)
POINT = re.compile(r"^\s*(?:point\s+)?(\d+)\s*[.:)]?\s+(passed|short|undecided)\b[\s:,.-]*(.*?)\.?\s*$", re.IGNORECASE)


@dataclass(frozen=True)
class ReviewReport:
    """A reviewer's report as it wrote it, and the points it names, each passed, short with why or undecided with why, in its order; it signs the work off when it passes every point of the brief, and leaves it to the agent when no point is short but one is undecided or not named."""

    text: str

    def points(self) -> tuple[ReviewPoint, ...]:
        matches = (POINT.match(line) for line in LINE_BREAK.split(self.text))
        return tuple(ReviewPoint(int(match[1]), PointVerdict(match[2].lower()), match[3]) for match in matches if match)

    def judged(self, verdict: PointVerdict) -> tuple[ReviewPoint, ...]:
        return tuple(point for point in self.points() if point.verdict == verdict)

    def is_approved(self, count: int) -> bool:
        return {point.number for point in self.judged(PointVerdict.PASSED)} >= set(range(1, count + 1)) and not self.judged(PointVerdict.SHORT)

    def is_undecided(self, count: int) -> bool:
        return not self.judged(PointVerdict.SHORT) and not self.is_approved(count)
