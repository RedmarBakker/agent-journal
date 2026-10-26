from dataclasses import dataclass

from tests.simulation.sample import Sample
from tests.simulation.scenario import Scenario
from tests.simulation.trace_entry import TraceEntry

# today's measures (plan 1034, phase 1): the fitness score against its threshold, unsmoothed, and the load against its first notice, smoothed
SCORE_THRESHOLD = 70
LOAD_LEVEL = 0.8
LOAD_WINDOW_MINUTES, LOAD_HALF_LIFE_MINUTES = 30, 10
SETTLE_MARGIN_MINUTES = 20
BURST_GAP_MINUTES = 5
MEASURE_FEATURES = ("workers.load_", "workers.fitness", "workers.work_mode_fitness", "workers.builder_", "workers.orchestrator_", "workers.solo_")
NOTICE_KEYS = ("messages.",)


@dataclass(frozen=True)
class Settling:
    """How a run's measures settle, worked out from its trace and samples: for each burst of arrivals, the minutes from its last arrival until each measure is on and stays on, against that measure's limit (its window plus three half-lives, nought when unsmoothed, plus twenty minutes); the band changes an hour; the measure lines an hour and every line but a refusal or a message notice an hour; and the mean score."""

    scenario: Scenario
    trace: tuple[TraceEntry, ...]
    samples: tuple[Sample, ...]
    profile: object

    def limits(self) -> dict[str, float]:
        return {"score": SETTLE_MARGIN_MINUTES, "load": LOAD_WINDOW_MINUTES + 3 * LOAD_HALF_LIFE_MINUTES + SETTLE_MARGIN_MINUTES}

    def is_on(self, measure: str, sample: Sample) -> bool:
        if measure == "load":
            return sample.rho <= LOAD_LEVEL
        scored = self.profile.scored(sample.counts)
        return not scored.is_measured or scored.score >= SCORE_THRESHOLD

    def last_arrivals(self) -> list[int]:
        minutes = sorted(at for at, _ in self.scenario.arrivals) or [0]
        return [minute for index, minute in enumerate(minutes) if index == len(minutes) - 1 or minutes[index + 1] - minute >= BURST_GAP_MINUTES]

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
        return {measure: [self.settle_minutes(measure, minute) for minute in self.last_arrivals()] for measure in self.limits()}

    def failures(self) -> list[str]:
        failing = [f"{measure} never settles after the burst ending at minute {burst}" if minutes is None else f"{measure} settles {minutes:.0f} minutes after the burst ending at minute {burst}, past its {self.limits()[measure]:.0f}"
                   for measure, settles in self.settled().items() for burst, minutes in zip(self.last_arrivals(), settles) if minutes is None or minutes > self.limits()[measure]]
        if self.band_changes_hourly() > 1:
            failing.append(f"the band changes {self.band_changes_hourly():.1f} times an hour, past 1")
        if self.measure_lines_hourly() > 6:
            failing.append(f"{self.measure_lines_hourly():.1f} measure lines an hour, past 6")
        if self.lines_hourly() > 10:
            failing.append(f"{self.lines_hourly():.1f} lines an hour that are neither refusals nor message notices, past 10")
        return failing

    def hours(self) -> float:
        return max(self.trace[-1].second / 3600, 1 / 60) if self.trace else 1.0

    def band_changes_hourly(self) -> float:
        levels = [sample.rho > LOAD_LEVEL for sample in self.samples]
        return sum(1 for before, after in zip(levels, levels[1:]) if before != after) / self.hours()

    def measure_lines_hourly(self) -> float:
        return sum(1 for entry in self.trace for key in entry.nudges if key.startswith(MEASURE_FEATURES)) / self.hours()

    def lines_hourly(self) -> float:
        return sum(1 for entry in self.trace if not entry.refused for key in entry.nudges if not key.startswith(NOTICE_KEYS)) / self.hours()

    def mean_score(self) -> float:
        scores = [scored.score for sample in self.samples if (scored := self.profile.scored(sample.counts)).is_measured]
        return sum(scores) / len(scores) if scores else 0.0
