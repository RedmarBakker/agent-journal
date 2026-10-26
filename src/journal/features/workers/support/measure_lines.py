from collections.abc import Callable

from journal.events.feature_data import FeatureData
from journal.engine.nudge import Nudge
from journal.features.tasks.tasks_part import TasksPart
from journal.features.workers.support.line_bands import LineBands
from journal.features.workers.workers_nudges import WorkersNudges
from journal.features.workers.workers_part import WorkersPart
from journal.models.support.measure_state import MeasureState

WORKER_REF = "workers:"


class MeasureLines:
    """The one line of each failing measure of the agent's mode that has one and speaks in the agent's band, made from the measure's state and the reading of the workers and the tasks; none where the line has no single action to name; and the measure a sent line belongs to."""

    @staticmethod
    def lines(data: FeatureData) -> tuple[Nudge, ...]:
        workers, makers = data.part(WorkersPart), MeasureLines.makers()
        mode = workers.measures.mode
        lines = (line for state in workers.measures.states if state.is_failing and (mode, state.key) in makers for line in makers[mode, state.key](state, data))
        return tuple(line for line in lines if LineBands.is_allowed(mode, line.key, workers.band))

    @staticmethod
    def handover_lines(data: FeatureData) -> tuple[Nudge, ...]:
        workers = data.part(WorkersPart)
        state = workers.measures.state("active_workers")
        if not state.is_failing or not workers.delivered_workers or not LineBands.is_allowed(workers.measures.mode, WorkersNudges.BUILDER_WORKER_LINE.key, workers.band):
            return ()
        return (WorkersNudges.BUILDER_WORKER_LINE.create(count=round(state.value, 1), n=workers.delivered_workers[0].row_id),)

    @staticmethod
    def measure_key(nudge_key: str) -> str:
        keys = {WorkersNudges.CLEAR_OLDEST.key: "high_queue_minutes", WorkersNudges.BUILDER_QUEUE_LINE.key: "high_queue_minutes", WorkersNudges.BUILDER_CODE_SHARE_LINE.key: "own_code_share", WorkersNudges.BUILDER_WORKER_LINE.key: "active_workers"}
        return keys.get(nudge_key, "")

    @staticmethod
    def makers() -> dict[tuple[str, str], Callable[[MeasureState, FeatureData], tuple[Nudge, ...]]]:
        return {("builder", "own_code_share"): MeasureLines.code_share_line, ("builder", "high_queue_minutes"): MeasureLines.oldest_worker_line, ("orchestrator", "high_queue_minutes"): MeasureLines.queue_line}

    @staticmethod
    def code_share_line(state: MeasureState, data: FeatureData) -> tuple[Nudge, ...]:
        tasks = data.part(TasksPart)
        task = tasks.current_task or (tasks.next_open.id if tasks.next_open else 0)
        return (WorkersNudges.BUILDER_CODE_SHARE_LINE.create(share=round(state.value, 2), n=task),) if task else ()

    @staticmethod
    def oldest_worker_line(state: MeasureState, data: FeatureData) -> tuple[Nudge, ...]:
        refs = [ref for ref in data.part(WorkersPart).workload.waiting_refs if ref.startswith(WORKER_REF)]
        return (WorkersNudges.BUILDER_QUEUE_LINE.create(minutes=round(state.value), n=refs[0].removeprefix(WORKER_REF)),) if refs else ()

    @staticmethod
    def queue_line(state: MeasureState, data: FeatureData) -> tuple[Nudge, ...]:
        workload = data.part(WorkersPart).workload
        return (WorkersNudges.CLEAR_OLDEST.create(minutes=round(state.value), first=workload.oldest()),) if workload.waiting_refs else ()
