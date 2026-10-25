import re
from dataclasses import dataclass

from journal.features.reviewing.support.review_point import ReviewPoint

# a report's lines, one per point and one for the tests, written on lines of their own or as sentences one after another
LINE_BREAK = re.compile(r"\n|(?<=\.)\s+(?=\d+\s*[.:)]?\s+(?:passed|short)\b|tests?\b)", re.IGNORECASE)
POINT = re.compile(r"^\s*(?:point\s+)?(\d+)\s*[.:)]?\s+(passed|short)\b[\s:,.-]*(.*?)\.?\s*$", re.IGNORECASE)


@dataclass(frozen=True)
class ReviewReport:
    """A reviewer's report as it wrote it, and the points it names, each passed or short with why, in its order."""

    text: str

    def points(self) -> tuple[ReviewPoint, ...]:
        matches = (POINT.match(line) for line in LINE_BREAK.split(self.text))
        return tuple(ReviewPoint(int(match[1]), match[2].lower() == "passed", match[3]) for match in matches if match)
