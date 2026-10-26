from collections.abc import Callable

from journal.engine.nudge import Nudge
from journal.engine.support.settings import Settings
from journal.events.feature_data import FeatureData
from journal.features.tasks.tasks_part import TasksPart
from journal.features.workers.support.line_bands import LineBands
from journal.features.workers.workers_nudges import WorkersNudges
from journal.features.workers.workers_options import WorkersOptions
from journal.features.workers.workers_part import WorkersPart
from journal.models.support.measure_state import MeasureState

WORKER_REF = "workers:"
LEAST_OPEN_TASKS = 2


class MeasureLines:
    """The one line of each failing measure of the agent's mode that has one and speaks in the agent's band, made from the measure's state, the reading of the workers and the tasks and the settings, each line once however many of its measures fail; none where the line has no single action to name; the lines a dispatch or a queue hears, and those a dispatch alone hears; and the measure a sent line belongs to."""

    @staticmethod
    def lines(data: FeatureData, settings: Settings) -> tuple[Nudge, ...]:
        workers, makers = data.part(WorkersPart), MeasureLines.makers()
        mode = workers.measures.mode
        candidates = (line for state in workers.measures.states if state.is_failing and (mode, state.key) in makers for line in makers[mode, state.key](state, data, settings))
        lines = {line.key: line for line in candidates if LineBands.is_allowed(mode, line.key, workers.band)}
        return tuple(lines.values())

    @staticmethod
    def handover_lines(data: FeatureData) -> tuple[Nudge, ...]:
        workers = data.part(WorkersPart)
        state = workers.measures.state("active_workers")
        if not state.is_failing or not workers.delivered_workers:
            return ()
        return MeasureLines.allowed(workers, WorkersNudges.BUILDER_WORKER_LINE.create(count=round(state.value, 1), n=workers.delivered_workers[0].row_id))

    @staticmethod
    def dispatch_lines(data: FeatureData) -> tuple[Nudge, ...]:
        workers = data.part(WorkersPart)
        refs = MeasureLines.worker_refs(workers)
        return MeasureLines.allowed(workers, WorkersNudges.ORCHESTRATOR_DISPATCH_LINE.create(n=refs[0])) if refs else ()

    @staticmethod
    def allowed(workers, line: Nudge) -> tuple[Nudge, ...]:
        return (line,) if LineBands.is_allowed(workers.measures.mode, line.key, workers.band) else ()

    @staticmethod
    def measure_key(nudge_key: str) -> str:
        keys = {WorkersNudges.ORCHESTRATOR_QUEUE_LINE.key: "high_queue_minutes", WorkersNudges.BUILDER_QUEUE_LINE.key: "high_queue_minutes", WorkersNudges.BUILDER_CODE_SHARE_LINE.key: "own_code_share",
                WorkersNudges.BUILDER_WORKER_LINE.key: "active_workers", WorkersNudges.ORCHESTRATOR_WAIT_LINE.key: "clearing_wait", WorkersNudges.ORCHESTRATOR_HANDOUT_LINE.key: "delegation",
                WorkersNudges.ORCHESTRATOR_REPORT_LINE.key: "report_share"}
        return keys.get(nudge_key, "")

    @staticmethod
    def makers() -> dict[tuple[str, str], Callable[[MeasureState, FeatureData, Settings], tuple[Nudge, ...]]]:
        return {("builder", "own_code_share"): MeasureLines.code_share_line, ("builder", "high_queue_minutes"): MeasureLines.oldest_worker_line, ("orchestrator", "high_queue_minutes"): MeasureLines.queue_line,
                ("orchestrator", "clearing_wait"): MeasureLines.wait_line, ("orchestrator", "delegation"): MeasureLines.handout_line, ("orchestrator", "idle_places"): MeasureLines.handout_line,
                ("orchestrator", "report_share"): MeasureLines.report_line}

    @staticmethod
    def worker_refs(workers) -> list[str]:
        return [ref.removeprefix(WORKER_REF) for ref in workers.workload.waiting_refs if ref.startswith(WORKER_REF)]

    @staticmethod
    def code_share_line(state: MeasureState, data: FeatureData, settings: Settings) -> tuple[Nudge, ...]:
        tasks = data.part(TasksPart)
        task = tasks.current_task or (tasks.next_open.id if tasks.next_open else 0)
        return (WorkersNudges.BUILDER_CODE_SHARE_LINE.create(share=round(state.value, 2), n=task),) if task else ()

    @staticmethod
    def oldest_worker_line(state: MeasureState, data: FeatureData, settings: Settings) -> tuple[Nudge, ...]:
        refs = MeasureLines.worker_refs(data.part(WorkersPart))
        return (WorkersNudges.BUILDER_QUEUE_LINE.create(minutes=round(state.value), n=refs[0]),) if refs else ()

    @staticmethod
    def queue_line(state: MeasureState, data: FeatureData, settings: Settings) -> tuple[Nudge, ...]:
        refs = MeasureLines.worker_refs(data.part(WorkersPart))
        return (WorkersNudges.ORCHESTRATOR_QUEUE_LINE.create(minutes=round(state.value), n=refs[0]),) if refs else ()

    @staticmethod
    def wait_line(state: MeasureState, data: FeatureData, settings: Settings) -> tuple[Nudge, ...]:
        refs = MeasureLines.worker_refs(data.part(WorkersPart))
        return (WorkersNudges.ORCHESTRATOR_WAIT_LINE.create(n=refs[0], minutes=round(state.value)),) if refs else ()

    @staticmethod
    def handout_line(state: MeasureState, data: FeatureData, settings: Settings) -> tuple[Nudge, ...]:
        workers, task = data.part(WorkersPart), data.part(TasksPart).next_open
        if task is None:
            return ()
        if workers.idle_workers:
            return (WorkersNudges.ORCHESTRATOR_HANDOUT_LINE.create(handout=f"queue task {task.id} to worker {workers.idle_workers[0].row_id}"),)
        has_place = len(workers.dispatched_workers) < settings.integer(WorkersOptions.WORKER_LIMIT)
        return (WorkersNudges.ORCHESTRATOR_HANDOUT_LINE.create(handout=f"dispatch a worker on task {task.id}"),) if has_place else ()

    @staticmethod
    def report_line(state: MeasureState, data: FeatureData, settings: Settings) -> tuple[Nudge, ...]:
        workers, tasks = data.part(WorkersPart), data.part(TasksPart)
        if not workers.dispatched_workers or tasks.open_count < LEAST_OPEN_TASKS:
            return ()
        return (WorkersNudges.ORCHESTRATOR_REPORT_LINE.create(tasks=round(1 / state.value, 1) if state.value else 0, n=workers.dispatched_workers[0].row_id),)
