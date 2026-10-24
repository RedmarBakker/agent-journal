import threading

from journal.models.timing import Timing
from journal.repositories.statistics import Statistics
from journal.repositories.setting_rows import SettingRows
from journal.repositories.timings import Timings
from journal.support.actor import Actor
from journal.support.stage_times import StageTimes
from journal.features.faults.faults_options import FaultsOptions

STAGES_PREFIX = "developer.stages."


class DeveloperTally:
    """The developer numbers of the requests answered since they were last written, stored in memory and written together: the sums to add to each series, the slowest time of each, and the timings."""

    def __init__(self, statistics: Statistics, timings: Timings, stages: StageTimes, settings: SettingRows) -> None:
        self.statistics, self.timings, self.stages, self.settings = statistics, timings, stages, settings
        self._lock = threading.Lock()
        self._sums: dict[str, int] = {}
        self._slowest: dict[str, int] = {}
        self._timings: list[Timing] = []

    def measured(self, prefix: str, ms: int) -> None:
        with self._lock:
            self._sums[f"{prefix}.count"] = self._sums.get(f"{prefix}.count", 0) + 1
            self._sums[f"{prefix}.total_ms"] = self._sums.get(f"{prefix}.total_ms", 0) + ms
            self._slowest[f"{prefix}.slowest_ms"] = max(ms, self._slowest.get(f"{prefix}.slowest_ms", 0))

    def added(self, key: str, amount: int) -> None:
        with self._lock:
            self._sums[key] = self._sums.get(key, 0) + amount

    def stage_samples(self) -> None:
        samples = self.stages.drained()
        if not self.settings.option(FaultsOptions.STAGE_TIMING):
            return
        for stage, ms in samples:
            self.measured(f"{STAGES_PREFIX}{stage}", ms)

    def logged(self, timing: Timing) -> None:
        with self._lock:
            self._timings.append(timing)

    def write(self) -> None:
        self.stage_samples()
        with self._lock:
            sums, slowest, timings = self._sums, self._slowest, self._timings
            self._sums, self._slowest, self._timings = {}, {}, []
        for key, amount in sums.items():
            self.statistics.added(key, amount, Actor.system())
        for key, ms in slowest.items():
            self.statistics.raised(key, ms, Actor.system())
        for timing in timings:
            self.timings.logged(timing, Actor.system())
