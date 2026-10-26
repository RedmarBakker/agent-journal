from dataclasses import dataclass


@dataclass(frozen=True)
class MeasureState:
    """One fitness measure of the agent's mode as last worked out: its value, whether there was anything to measure, whether it is failing, past its range, when it last turned failing or passing, when its line was last sent and when it was measured."""

    key: str
    value: float = 0.0
    is_measured: bool = False
    is_failing: bool = False
    changed_at: float = 0.0
    last_line_at: float = 0.0
    measured_at: float = 0.0
