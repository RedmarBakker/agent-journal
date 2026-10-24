import threading

from journal.features.faults.faults_options import FaultsOptions
from journal.models.timing import Timing
from journal.repositories.setting_rows import SettingRows
from journal.support.stage_times import StageTimes

STAGES_PREFIX = "developer.stages."
LOG_ROWS = 1000


class DeveloperTally:
    """The developer numbers since the server booted, kept in memory and written nowhere: the count, total and slowest time of each series, the rows loaded per model, and the rolling log of the newest thousand timings."""

    def __init__(self, stages: StageTimes, settings: SettingRows) -> None:
        self.stages, self.settings = stages, settings
        self._lock = threading.Lock()
        self._numbers: dict[str, int] = {}
        self._log: list[Timing] = []

    def measured(self, prefix: str, ms: int) -> None:
        with self._lock:
            self._numbers[f"{prefix}.count"] = self._numbers.get(f"{prefix}.count", 0) + 1
            self._numbers[f"{prefix}.total_ms"] = self._numbers.get(f"{prefix}.total_ms", 0) + ms
            self._numbers[f"{prefix}.slowest_ms"] = max(ms, self._numbers.get(f"{prefix}.slowest_ms", 0))

    def added(self, key: str, amount: int) -> None:
        with self._lock:
            self._numbers[key] = self._numbers.get(key, 0) + amount

    def logged(self, timing: Timing) -> None:
        with self._lock:
            self._log.append(timing)
            del self._log[:-LOG_ROWS]

    def series(self, prefix: str) -> dict[str, int]:
        self.stage_samples()
        with self._lock:
            return {key: value for key, value in sorted(self._numbers.items()) if key.startswith(prefix)}

    def timings(self) -> list[Timing]:
        with self._lock:
            return list(reversed(self._log))

    def cleared(self) -> None:
        self.stage_samples()
        with self._lock:
            self._numbers.clear()
            self._log.clear()

    def stage_samples(self) -> None:
        samples = self.stages.drained()
        if not self.settings.option(FaultsOptions.STAGE_TIMING):
            return
        for stage, ms in samples:
            self.measured(f"{STAGES_PREFIX}{stage}", ms)
