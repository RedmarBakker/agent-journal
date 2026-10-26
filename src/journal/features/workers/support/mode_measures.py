from dataclasses import replace

from journal.features.workers.support.closeness import Closeness
from journal.features.workers.support.fitness_score import FitnessScore
from journal.features.workers.fitness_options import FitnessOptions
from journal.features.workers.support.free_place_measure import FreePlaceMeasure
from journal.features.workers.support.half_life import HalfLife
from journal.features.workers.support.measure_range import MeasureRange
from journal.features.workers.support.measure_source import MeasureSource
from journal.features.workers.support.measure_spec import MeasureSpec
from journal.features.workers.support.active_worker_measure import ActiveWorkerMeasure
from journal.features.workers.workers_options import WorkersOptions
from journal.models.agent import Agent
from journal.models.support.measure_state import MeasureState
from journal.models.support.measure_states import MeasureStates
from journal.repositories.setting_rows import SettingRows
from journal.repositories.tasks import Tasks

HIGH_QUEUE = MeasureSpec("high_queue_minutes", MeasureRange(10.0, 10.0), MeasureSource.high_queue_minutes, Closeness.minutes, 4, label="Minutes the worker queue stood high")
ACTIVE_WORKERS = MeasureSpec("active_workers", MeasureRange(2.0, 2.0), MeasureSource.active_worker_mean, Closeness.mean, 2, label="Workers active at once, on average")
SHOWN = MeasureRange(float("inf"), float("inf"))
BUILDER_SPECS = (MeasureSpec("own_code_share", MeasureRange(0.5, 0.6), MeasureSource.code_share, Closeness.share, 4, label="Your own share of the code"), HIGH_QUEUE)
COMPLETION_RATE = MeasureSpec("completion_rate", SHOWN, MeasureSource.completion_rate, Closeness.count, 0, label="Tasks completed an hour")
MESSAGE_WAIT = MeasureSpec("message_wait", MeasureRange(5.0, 5.0), MeasureSource.message_wait_minutes, Closeness.minutes, 3, label="Minutes the oldest message waited")
MODE_SPECS = {
    "solo": (MESSAGE_WAIT, COMPLETION_RATE),
}
ORCHESTRATOR_SPECS = (MeasureSpec("clearing_wait", MeasureRange(6.0, 6.0), MeasureSource.clearing_wait, Closeness.mean, 3, label="Minutes the oldest worker waited"), MeasureSpec("delegation", MeasureRange(0.3, 0.2), MeasureSource.delegation, Closeness.share, 3, label="Your own share of the landed code"),
                      MeasureSpec("idle_places", MeasureRange(5.0, 4.0), MeasureSource.idle_place_minutes, Closeness.minutes, 3, smoothing_minutes=15.0, label="Minutes a place stood free"),
                      MeasureSpec("report_share", MeasureRange(0.5, 0.34), MeasureSource.report_share, Closeness.mean, 2, label="First reports per merged task"),
                      MeasureSpec("oldest_first_share", SHOWN, MeasureSource.oldest_first_share, Closeness.share, 0, label="Share cleared oldest first"), MeasureSpec("rejection_share", SHOWN, MeasureSource.rejection_share, Closeness.share, 0, label="Share sent back"))
LINE_DELAY_MINUTES = 5.0
SCORE_VERSION = 2

class ModeMeasures:
    """Works out each fitness measure of the agent's mode from its series and its two queues: the value, smoothed where its spec says, whether there was anything to measure, and whether it is failing by the hysteresis of its levels, the orchestrator's queue held high failing five minutes after the place it opens; and the score from those states, each measured one's closeness weighted, once the mode has been measured for the warm-up."""

    def __init__(self, free_places: FreePlaceMeasure, active_workers: ActiveWorkerMeasure, tasks: Tasks, settings: SettingRows) -> None:
        self.free_places, self.active_workers, self.tasks, self.settings = free_places, active_workers, tasks, settings

    def specs(self, mode: str) -> tuple[MeasureSpec, ...]:
        line_minutes = self.settings.decimal(WorkersOptions.PLACE_OPENING_MINUTES) + LINE_DELAY_MINUTES
        orchestrator = (replace(HIGH_QUEUE, range=MeasureRange(line_minutes, line_minutes), weight=6), *ORCHESTRATOR_SPECS, MESSAGE_WAIT, COMPLETION_RATE)
        worker_limit = self.settings.decimal(FitnessOptions.BUILDER_ACTIVE_WORKERS)
        builder = (*BUILDER_SPECS, replace(ACTIVE_WORKERS, range=MeasureRange(worker_limit, worker_limit)), MESSAGE_WAIT, COMPLETION_RATE)
        return {**MODE_SPECS, "builder": builder, "orchestrator": orchestrator}.get(mode, ())

    def worked(self, agent: Agent, mode: str, time: float) -> MeasureStates:
        previous = agent.measures if agent.measures.mode == mode else MeasureStates(mode, time)
        source = MeasureSource(agent, time, self.free_places, self.active_workers, self.tasks, previous.started_at)
        return replace(previous, states=tuple(self.stepped(spec, previous.state(spec.key), spec.reader(source), time) for spec in self.specs(mode)))

    @staticmethod
    def scored(measures: MeasureStates, mode_specs: tuple[MeasureSpec, ...], warmup_seconds: float) -> FitnessScore:
        specs = {spec.key: spec for spec in mode_specs}
        weighed = [(specs[state.key], specs[state.key].closeness(state.value, specs[state.key].range)) for state in measures.states if state.is_measured and state.key in specs and specs[state.key].weight]
        if not weighed or measures.latest_time() - measures.started_at < warmup_seconds:
            return FitnessScore(measures.mode, 100, is_measured=False, version=SCORE_VERSION)
        score = round(100 * sum(spec.weight * closeness for spec, closeness in weighed) / sum(spec.weight for spec, _ in weighed))
        return FitnessScore(measures.mode, score, parts=tuple((spec.key, round(100 * closeness)) for spec, closeness in weighed), version=SCORE_VERSION)

    @staticmethod
    def stepped(spec: MeasureSpec, previous: MeasureState, raw: float | None, time: float) -> MeasureState:
        if raw is None:
            return replace(previous, is_measured=False, is_failing=False, changed_at=time if previous.is_failing else previous.changed_at, measured_at=time)
        value = HalfLife(spec.smoothing_minutes).folded(previous.value, raw, time - previous.measured_at) if spec.smoothing_minutes and previous.is_measured else raw
        is_failing = spec.range.is_failing(previous.is_failing, value)
        return replace(previous, value=round(value, 3), is_measured=True, is_failing=is_failing, changed_at=time if is_failing != previous.is_failing else previous.changed_at, measured_at=time)
