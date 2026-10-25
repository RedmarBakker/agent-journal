from dataclasses import dataclass

GOOD, BAD = "good", "bad"


@dataclass(frozen=True)
class ReviewPoint:
    """One point of a reviewer's report: its number, whether it passed, and why it fell short."""

    number: int
    passed: bool
    shortfall: str = ""

    def line(self) -> str:
        return f"Point {self.number} passed" if self.passed else f"Point {self.number} short: {self.shortfall}".rstrip(": ")

    def tone(self) -> str:
        return GOOD if self.passed else BAD
