from dataclasses import dataclass

from journal.features.workers.support.half_life import HalfLife
from journal.features.workers.support.load_item import LoadItem
from journal.features.workers.support.queue_walk import QueueWalk
from journal.models.support.agent_load import AgentLoad

STEP_SECONDS = 60.0
# how many half-lives of history the smoothing folds in before the measure, so what is older weighs under two per cent
HALF_LIVES = 6
# how far back a dispatch looks to see whether the queue was growing, in seconds
GROWTH_SECONDS = 300.0
# the oldest waiting items the load keeps the refs of on the agent's row; the rest it counts
WAITING_REFS_STORED = 8


@dataclass(frozen=True)
class LoadSeries:
    """The orchestrator measured as one server over its items, minute by minute: in each sliding window λ is the weight that arrived an hour, μ the weight cleared an hour of busy time, while something waited, and W the minutes from arrival to clearing of what was cleared; each smoothed with the half-life, μ only while something waits, ρ = λ/μ, μ counted as one clearing a window until one is measured, and L what waits now. The minutes ρ has stayed at or over the busy level while an item waited, or under the quiet level, end now; the clearings in the window are counted for taking the oldest waiting item first, and each dispatch in it for or against: against while the queue grew with ρ over the busy level, for while ρ was under the quiet level."""

    window_minutes: float
    half_life_minutes: float
    busy_at: float
    quiet_at: float

    def measured(self, items: list[LoadItem], dispatches: list[float], moment: float) -> AgentLoad:
        window = self.window_minutes * 60
        walk = self.walk(items, moment, window + HALF_LIVES * self.half_life_minutes * 60)
        series, arrivals, clearings, wait = list(walk.points), walk.arrivals, walk.clearings, walk.wait_minutes
        waiting = sum(item.weight for item in items if item.is_waiting(moment))
        rho = series[-1][1]
        counted = [item for item in items if item.is_cleared_in(moment - window, moment)]
        sorted_waiting = sorted((item for item in items if item.is_waiting(moment)), key=lambda item: (item.arrived_at, item.ref))
        calm_dispatches, busy_dispatches = self.dispatch_counts(series, [time for time in dispatches if moment - window < time <= moment])
        return AgentLoad(arrivals=round(arrivals, 2), clearings=round(clearings or 0.0, 2), rho=round(rho, 2), waiting=round(waiting, 2), waiting_refs=tuple(item.ref for item in sorted_waiting[:WAITING_REFS_STORED]), waiting_items=len(sorted_waiting), oldest_wait_minutes=round(sum((moment - item.arrived_at) / 60 for item in sorted_waiting[:1]), 2),
                         wait_minutes=round(wait or 0.0, 2), little=round(arrivals * (wait or 0.0) / 60, 2), over_minutes=self.stretch(series, lambda point: point[1] >= self.busy_at and point[2] > 0),
                         under_minutes=self.stretch(series, lambda point: point[1] < self.quiet_at), oldest_first=sum(1 for item in counted if self.was_oldest(items, item)),
                         clearings_counted=len(counted), removals=sum(1 for item in items if item.is_removal(moment - window, moment)), dispatches_for=calm_dispatches, dispatches_against=busy_dispatches, measured_at=moment)

    def walk(self, items: list[LoadItem], moment: float, horizon: float) -> QueueWalk:
        window = self.window_minutes * 60
        times = [moment - horizon + step * STEP_SECONDS for step in range(int(horizon // STEP_SECONDS) + 1)]
        if times[-1] < moment:
            times.append(moment)
        half_life = HalfLife(self.half_life_minutes)
        arrivals = clearings = wait = None
        series: list[tuple[float, float, float]] = []
        for time in times:
            raw_arrivals = self.arrived(items, time - window, time) / (window / 3600)
            arrivals = raw_arrivals if arrivals is None else half_life.folded(arrivals, raw_arrivals, STEP_SECONDS)
            busy = self.busy_seconds(items, time - window, time)
            waiting = sum(item.weight for item in items if item.is_waiting(time))
            if busy > 0 and waiting > 0:
                raw_clearings = self.cleared(items, time - window, time) / (busy / 3600)
                clearings = raw_clearings if clearings is None else half_life.folded(clearings, raw_clearings, STEP_SECONDS)
            raw_wait = self.waited(items, time - window, time)
            if raw_wait is not None:
                wait = raw_wait if wait is None else half_life.folded(wait, raw_wait, STEP_SECONDS)
            series.append((time, arrivals / (clearings or self.least_clearings()), waiting))
        return QueueWalk(tuple(series), arrivals, clearings, wait)

    @staticmethod
    def arrived(items: list[LoadItem], start: float, end: float) -> float:
        return sum(item.weight for item in items if start < item.arrived_at <= end)

    @staticmethod
    def cleared(items: list[LoadItem], start: float, end: float) -> float:
        return sum(item.weight for item in items if item.is_cleared_in(start, end))

    @staticmethod
    def waited(items: list[LoadItem], start: float, end: float) -> float | None:
        cleared = [item for item in items if item.is_cleared_in(start, end)]
        weight = sum(item.weight for item in cleared)
        return sum(item.weight * (item.cleared_at - item.arrived_at) / 60 for item in cleared) / weight if weight else None

    @staticmethod
    def busy_seconds(items: list[LoadItem], start: float, end: float) -> float:
        spans = sorted((max(item.arrived_at, start), min(item.cleared_at or end, end)) for item in items if item.arrived_at < end and (item.cleared_at or end) > start)
        total, reached = 0.0, start
        for begin, finish in spans:
            if finish > reached:
                total += finish - max(begin, reached)
                reached = finish
        return total

    def least_clearings(self) -> float:
        return 60 / self.window_minutes

    @staticmethod
    def stretch(series: list[tuple[float, float, float]], holds) -> float:
        if not holds(series[-1]):
            return 0.0
        first_time = series[-1][0]
        for point in reversed(series):
            if not holds(point):
                break
            first_time = point[0]
        return round((series[-1][0] - first_time) / 60, 1)

    @staticmethod
    def was_oldest(items: list[LoadItem], item: LoadItem) -> bool:
        before = item.cleared_at - 1e-6
        waiting = [other for other in items if other.is_waiting(before)]
        return bool(waiting) and min(waiting, key=lambda other: (other.arrived_at, other.ref)) == item

    def dispatch_counts(self, series: list[tuple[float, float, float]], dispatches: list[float]) -> tuple[int, int]:
        calm_count = busy_count = 0
        for time in dispatches:
            current, base = self.point(series, time), self.point(series, time - GROWTH_SECONDS)
            busy_count += current[1] > self.busy_at and current[2] > base[2]
            calm_count += current[1] < self.quiet_at
        return calm_count, busy_count

    @staticmethod
    def point(series: list[tuple[float, float, float]], time: float) -> tuple[float, float, float]:
        return next((point for point in reversed(series) if point[0] <= time), series[0])
