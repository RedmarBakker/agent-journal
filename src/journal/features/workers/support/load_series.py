from dataclasses import dataclass

from journal.features.workers.support.load_item import LoadItem
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
    """The orchestrator measured as one server over its items, minute by minute: in each sliding window λ is the weight that arrived an hour, μ the weight cleared an hour of busy time, while something waited, and W the minutes from arrival to clearing of what was cleared; each smoothed with the half-life, μ only while something waits, ρ = λ/μ, μ counted as one clearing a window until one is measured, and L what waits now. The minutes ρ has stayed over the busy level or under the quiet level end now; the clearings in the window are counted for taking the oldest waiting item first, and each dispatch in it for or against: against while the queue grew with ρ over the busy level, for while ρ was under the quiet level."""

    window_minutes: float
    half_life_minutes: float
    busy_at: float
    quiet_at: float

    def measured(self, items: list[LoadItem], dispatches: list[float], now: float) -> AgentLoad:
        window = self.window_minutes * 60
        horizon = window + HALF_LIVES * self.half_life_minutes * 60
        times = [now - horizon + step * STEP_SECONDS for step in range(int(horizon // STEP_SECONDS) + 1)]
        if times[-1] < now:
            times.append(now)
        alpha = 1 - 0.5 ** (STEP_SECONDS / (self.half_life_minutes * 60))
        arrivals = clearings = wait = None
        series: list[tuple[float, float, float]] = []
        for time in times:
            raw_arrivals = self.arrived(items, time - window, time) / (window / 3600)
            arrivals = raw_arrivals if arrivals is None else arrivals + alpha * (raw_arrivals - arrivals)
            busy = self.busy_seconds(items, time - window, time)
            waiting = sum(item.weight for item in items if item.is_waiting(time))
            if busy > 0 and waiting > 0:
                raw_clearings = self.cleared(items, time - window, time) / (busy / 3600)
                clearings = raw_clearings if clearings is None else clearings + alpha * (raw_clearings - clearings)
            raw_wait = self.waited(items, time - window, time)
            if raw_wait is not None:
                wait = raw_wait if wait is None else wait + alpha * (raw_wait - wait)
            series.append((time, arrivals / (clearings or self.least_clearings()), waiting))
        waiting = sum(item.weight for item in items if item.is_waiting(now))
        rho = series[-1][1]
        counted = [item for item in items if item.is_cleared_in(now - window, now)]
        sorted_waiting = sorted((item for item in items if item.is_waiting(now)), key=lambda item: (item.arrived_at, item.ref))
        for_, against = self.dispatch_counts(series, [time for time in dispatches if now - window < time <= now])
        return AgentLoad(arrivals=round(arrivals, 2), clearings=round(clearings or 0.0, 2), rho=round(rho, 2), waiting=round(waiting, 2), waiting_refs=tuple(item.ref for item in sorted_waiting[:WAITING_REFS_STORED]), waiting_items=len(sorted_waiting),
                         wait_minutes=round(wait or 0.0, 2), little=round(arrivals * (wait or 0.0) / 60, 2), over_minutes=self.stretch(series, lambda value: value > self.busy_at),
                         under_minutes=self.stretch(series, lambda value: value < self.quiet_at), oldest_first=sum(1 for item in counted if self.was_oldest(items, item)),
                         clearings_counted=len(counted), dispatches_for=for_, dispatches_against=against, measured_at=now)

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
        start = series[-1][0]
        for time, rho, _ in reversed(series):
            if not holds(rho):
                break
            start = time
        return round((series[-1][0] - start) / 60, 1) if holds(series[-1][1]) else 0.0

    @staticmethod
    def was_oldest(items: list[LoadItem], item: LoadItem) -> bool:
        before = item.cleared_at - 1e-6
        waiting = [other for other in items if other.is_waiting(before)]
        return bool(waiting) and min(waiting, key=lambda other: (other.arrived_at, other.ref)) == item

    def dispatch_counts(self, series: list[tuple[float, float, float]], dispatches: list[float]) -> tuple[int, int]:
        at = lambda time: next((point for point in reversed(series) if point[0] <= time), series[0])
        for_ = against = 0
        for time in dispatches:
            _, rho, waiting = at(time)
            _, _, earlier = at(time - GROWTH_SECONDS)
            against += rho > self.busy_at and waiting > earlier
            for_ += rho < self.quiet_at
        return for_, against
