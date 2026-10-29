from collections.abc import Callable
from dataclasses import dataclass

from journal.features.workers.support.fitness_score import FitnessScore
from journal.models.support.measure_states import MeasureStates
from journal.models.support.pressure_band import PressureBand

from tests.simulation.sample import Sample
from tests.simulation.scenario import Scenario
from tests.simulation.trace_entry import TraceEntry

# the fitness score from the measure states against its threshold, and the work load against its first notice, smoothed
SCORE_THRESHOLD = 70
LOAD_LEVEL = 0.8
LOAD_WINDOW_MINUTES, LOAD_HALF_LIFE_MINUTES = 30, 10
SETTLE_MARGIN_MINUTES = 20
BURST_GAP_MINUTES = 5
MEASURE_FEATURES = ("workers.builder_", "workers.orchestrator_", "workers.solo_")
# lines that report an event of the agent's own work loop, a message of the user's, a worker's delivery or a worker left without work, not counted against the quiet limit
NOTICE_KEYS = ("messages.", "workers.work_ready", "workers.worker_has_no_work_left")


@dataclass(frozen=True)
class Settling:
    """How a run's measures settle, worked out from its trace and samples: for each burst of arrivals, those closer together than the measure's limit being one burst, since a measure cannot settle before the next arrival lands, and no burst for the load in a scenario with no arrivals, whose load is the agent's own work, the minutes from its last arrival until each measure is on and stays on, against that measure's limit (its window plus three half-lives, nought when unsmoothed, plus twenty minutes); the band changes an hour, its first measuring out of no band not counted; the measure lines an hour, of every line the agent heard in any hook of an action, and every other feature's line but a refusal or a notice of the agent's work loop an hour, the measure lines having their own limit; and the mean score."""

    scenario: Scenario
    trace: tuple[TraceEntry, ...]
    samples: tuple[Sample, ...]
    scoring: Callable[[MeasureStates], FitnessScore]
    keys_heard: tuple[str, ...]

    def limits(self) -> dict[str, float]:
        return {"score": SETTLE_MARGIN_MINUTES, "load": LOAD_WINDOW_MINUTES + 3 * LOAD_HALF_LIFE_MINUTES + SETTLE_MARGIN_MINUTES}

    def is_on(self, measure: str, sample: Sample) -> bool:
        if measure == "load":
            return sample.rho <= LOAD_LEVEL
        scored = self.scoring(sample.measures)
        return not scored.is_measured or scored.score >= SCORE_THRESHOLD

    def last_arrivals(self, measure: str, limit_minutes: float) -> list[int]:
        minutes = sorted(minute for minute, _ in self.scenario.arrivals) or self.unburst_start(measure)
        return [minute for index, minute in enumerate(minutes) if index == len(minutes) - 1 or minutes[index + 1] - minute >= max(BURST_GAP_MINUTES, limit_minutes)]

    @staticmethod
    def unburst_start(measure: str) -> list[int]:
        return [] if measure == "load" else [0]

    def settle_minutes(self, measure: str, after_minute: int) -> float | None:
        later = [sample for sample in self.samples if sample.second >= after_minute * 60]
        off = [sample.second for sample in later if not self.is_on(measure, sample)]
        if not later:
            return None
        if not off:
            return 0.0
        if off[-1] == later[-1].second:
            return None
        return (off[-1] - after_minute * 60) / 60

    def settled(self) -> dict[str, list[float | None]]:
        return {measure: [self.settle_minutes(measure, minute) for minute in self.last_arrivals(measure, limit)] for measure, limit in self.limits().items()}

    def failures(self) -> list[str]:
        failing = [f"{measure} never settles after the burst ending at minute {burst}" if minutes is None else f"{measure} settles {minutes:.0f} minutes after the burst ending at minute {burst}, past its {self.limits()[measure]:.0f}"
                   for measure, settles in self.settled().items() for burst, minutes in zip(self.last_arrivals(measure, self.limits()[measure]), settles) if minutes is None or minutes > self.limits()[measure]]
        if self.band_changes_hourly() > 1:
            failing.append(f"the band changes {self.band_changes_hourly():.1f} times an hour, past 1")
        if self.measure_lines_hourly() > 6:
            failing.append(f"{self.measure_lines_hourly():.1f} measure lines an hour, past 6")
        if self.lines_hourly() > 10:
            failing.append(f"{self.lines_hourly():.1f} lines an hour from other features that are neither refusals nor notices of the agent's work loop, past 10")
        return failing

    def hours(self) -> float:
        return max(self.trace[-1].second / 3600, 1 / 60) if self.trace else 1.0

    def band_changes_hourly(self) -> float:
        bands = [sample.band for sample in self.samples if sample.band != PressureBand.NONE]
        return sum(1 for previous_band, band in zip(bands, bands[1:]) if previous_band != band) / self.hours()

    def measure_lines_hourly(self) -> float:
        return sum(1 for key in self.keys_heard if key.startswith(MEASURE_FEATURES)) / self.hours()

    def lines_hourly(self) -> float:
        return sum(1 for entry in self.trace if not entry.refused for key in entry.nudges if not key.startswith(NOTICE_KEYS + MEASURE_FEATURES)) / self.hours()

    def mean_score(self) -> float:
        scores = [scored.score for sample in self.samples if (scored := self.scoring(sample.measures)).is_measured]
        return sum(scores) / len(scores) if scores else 0.0
