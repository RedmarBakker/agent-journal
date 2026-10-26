from dataclasses import dataclass, replace

from journal.models.support.measure_state import MeasureState


@dataclass(frozen=True)
class MeasureStates:
    """The fitness measures of the agent's mode as last worked out: the mode, when its measuring began, and one state per measure."""

    mode: str = ""
    started_at: float = 0.0
    states: tuple[MeasureState, ...] = ()

    @classmethod
    def parsed(cls, data: dict) -> "MeasureStates":
        return cls(data.get("mode", ""), float(data.get("started_at", 0.0)), tuple(MeasureState(**state) for state in data.get("states", ())))

    def state(self, key: str) -> MeasureState:
        return next((state for state in self.states if state.key == key), MeasureState(key))

    def failing_keys(self) -> tuple[str, ...]:
        return tuple(state.key for state in self.states if state.is_failing)

    def line_sent(self, key: str, time: float) -> "MeasureStates":
        return replace(self, states=tuple(replace(state, last_line_at=time) if state.key == key else state for state in self.states))

    def latest_time(self) -> float:
        return max((state.measured_at for state in self.states), default=0.0)
