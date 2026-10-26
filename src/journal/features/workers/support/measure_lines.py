from collections.abc import Callable

from journal.engine.nudge import Nudge
from journal.features.workers.support.line_bands import LineBands
from journal.features.workers.support.workers_data import WorkersData
from journal.features.workers.workers_nudges import WorkersNudges
from journal.models.support.measure_state import MeasureState


class MeasureLines:
    """The one line of each failing measure that has one and speaks in the agent's band, made from the measure's state and the workers' reading; none where the line has no single action to name; and the measure a sent line belongs to."""

    @staticmethod
    def lines(workers: WorkersData) -> tuple[Nudge, ...]:
        makers = MeasureLines.makers()
        lines = (line for state in workers.measures.states if state.is_failing and state.key in makers for line in makers[state.key](state, workers))
        return tuple(line for line in lines if LineBands.is_allowed(workers.measures.mode, line.key, workers.band))

    @staticmethod
    def measure_key(nudge_key: str) -> str:
        return {WorkersNudges.CLEAR_OLDEST.key: "high_queue_minutes"}.get(nudge_key, "")

    @staticmethod
    def makers() -> dict[str, Callable[[MeasureState, WorkersData], tuple[Nudge, ...]]]:
        return {"high_queue_minutes": MeasureLines.clear_oldest}

    @staticmethod
    def clear_oldest(state: MeasureState, workers: WorkersData) -> tuple[Nudge, ...]:
        return (WorkersNudges.CLEAR_OLDEST.create(minutes=round(state.value), first=workers.workload.oldest()),) if workers.workload.waiting_refs else ()
