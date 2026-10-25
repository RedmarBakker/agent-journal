from dataclasses import dataclass


@dataclass(frozen=True)
class FitnessGap:
    """A measure an agent is off its mode's ideal on: what it measures, the value the agent shows, the range an ideal agent keeps, what to do about it, and the unit the value and the range are in."""

    label: str
    percent: int
    low: int
    high: int
    advice: str
    unit: str = "%"

    def text(self) -> str:
        return f"{self.label} is {self.percent}{self.unit}, ideal {self.low}-{self.high}{self.unit}: {self.advice}"
