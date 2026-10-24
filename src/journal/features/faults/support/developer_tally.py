import threading
import time

from journal.features.faults.faults_options import FaultsOptions
from journal.models.support.request_loads import RequestLoads
from journal.models.timing import Timing
from journal.repositories.setting_rows import SettingRows
from journal.support.stage_times import StageTimes

STAGES_PREFIX = "developer.stages."
LOG_ROWS = 1000
ROLLING_ROWS = 250
POINTS_GROUP = "developer.points"
# how far back the bar's averages reach: an answer older than this counts no more, however few came since
WINDOW_SECONDS = 15 * 60


class DeveloperTally:
    """The developer numbers since the server booted, kept in memory and written nowhere: the count, total and slowest time of each series, the rows loaded per model, and the rolling log of the newest thousand timings, and the newest 250 timings of each hook kind and each route within the last fifteen minutes, whose averages are averaged so a frequent cheap one counts as much as a rare dear one."""

    def __init__(self, stages: StageTimes, settings: SettingRows) -> None:
        self.stages, self.settings = stages, settings
        self._lock = threading.Lock()
        self._numbers: dict[str, int] = {}
        self._log: list[Timing] = []
        self._rolling: dict[str, dict[str, list[tuple[float, int]]]] = {}
        self._loads: dict[str, list[tuple[float, RequestLoads]]] = {}

    def measured(self, prefix: str, ms: int) -> None:
        with self._lock:
            self._numbers[f"{prefix}.count"] = self._numbers.get(f"{prefix}.count", 0) + 1
            self._numbers[f"{prefix}.total_ms"] = self._numbers.get(f"{prefix}.total_ms", 0) + ms
            self._numbers[f"{prefix}.slowest_ms"] = max(ms, self._numbers.get(f"{prefix}.slowest_ms", 0))

    def windowed(self, group: str, kind: str, ms: int) -> None:
        with self._lock:
            window = self._rolling.setdefault(group, {}).setdefault(kind, [])
            window.append((time.monotonic(), ms))
            del window[:-ROLLING_ROWS]

    def loaded(self, kind: str, loads: RequestLoads) -> None:
        with self._lock:
            window = self._loads.setdefault(kind, [])
            window.append((time.monotonic(), loads))
            del window[:-ROLLING_ROWS]

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

    def rolling_average(self, group: str) -> int:
        with self._lock:
            kind_averages = [sum(window) / len(window) for window in self.recent_windows(group).values()]
            return round(sum(kind_averages) / len(kind_averages)) if kind_averages else 0

    def rolling_parts(self, group: str) -> list[dict]:
        with self._lock:
            parts = [{"name": kind, "average": round(sum(window) / len(window)), "count": len(window), "details": self.time_details(window)} for kind, window in self.recent_windows(group).items()]
        return sorted(parts, key=lambda part: -part["average"])

    def recent_windows(self, group: str) -> dict[str, list[int]]:
        windows = {kind: self.recent(window) for kind, window in self._rolling.get(group, {}).items()}
        return {kind: window for kind, window in windows.items() if window}

    @staticmethod
    def recent(window: list) -> list:
        start = time.monotonic() - WINDOW_SECONDS
        return [value for moment, value in window if moment >= start]

    @staticmethod
    def time_details(window: list[int]) -> list[dict]:
        return [{"label": "Average", "text": f"{round(sum(window) / len(window))} ms"}, {"label": "Slowest", "text": f"{max(window)} ms"}, {"label": "Newest", "text": f"{window[-1]} ms"}]

    def point_parts(self) -> list[dict]:
        with self._lock:
            parts = [{"name": kind, "average": round(sum(window) / len(window)), "count": len(window), "details": self.table_details(self.recent(self._loads.get(kind, [])))} for kind, window in self.recent_windows(POINTS_GROUP).items()]
        return sorted(parts, key=lambda part: -part["average"])

    @staticmethod
    def table_details(answers: list[RequestLoads]) -> list[dict]:
        totals: dict[str, list[int]] = {}
        for answer in answers:
            for load in answer.counts:
                total = totals.setdefault(load.model, [0, 0, 0])
                total[0], total[1], total[2] = total[0] + load.rows, total[1] + load.bytes, total[2] + load.writes
        each = lambda amount: f"{amount / len(answers):.1f}".removesuffix(".0")
        ranked = sorted(totals.items(), key=lambda item: -(item[1][0] + item[1][2] + item[1][1] / 1024))
        return [{"label": table, "text": f"{each(rows)} rows, {each(size / 1024)} KB, {each(writes)} writes"} for table, (rows, size, writes) in ranked]

    def timings(self) -> list[Timing]:
        with self._lock:
            return list(reversed(self._log))

    def cleared(self) -> None:
        self.stage_samples()
        with self._lock:
            self._numbers.clear()
            self._log.clear()
            self._rolling.clear()
            self._loads.clear()

    def stage_samples(self) -> None:
        samples = self.stages.drained()
        if not self.settings.option(FaultsOptions.STAGE_TIMING):
            return
        for stage, ms in samples:
            self.measured(f"{STAGES_PREFIX}{stage}", ms)
