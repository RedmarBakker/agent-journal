from dataclasses import dataclass


@dataclass(frozen=True)
class FitnessGap:
    """A measure an agent is off its mode's ideal on: what it measures, the share the agent shows, the range an ideal agent keeps, and what to do about it."""

    label: str
    percent: int
    low: int
    high: int
    advice: str

    def text(self) -> str:
        return f"{self.label} is {self.percent}%, ideal {self.low}-{self.high}%: {self.advice}"
