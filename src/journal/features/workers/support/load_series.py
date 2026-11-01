from dataclasses import dataclass

from journal.features.workers.support.half_life import HalfLife
from journal.features.workers.support.load_item import LoadItem
from journal.features.workers.support.queue_walk import QueueWalk
from journal.models.support.agent_load import AgentLoad

STEP_SECONDS = 60.0
# how many half-lives of history the smoothing folds in before the measure, so what is older weighs under two per cent
HALF_LIVES = 6
# how far back a dispatch looks to see whether the queue was growing, in seconds
# the oldest waiting items the load keeps the refs of on the agent's row; the rest it counts
WAITING_REFS_STORED = 8


@dataclass(frozen=True)
class LoadSeries:
    """The worker or message queue's arrival rate, clearing rate and waiting time, smoothed over a sliding window, with the busy and quiet stretches used to scale worker places."""

    window_minutes: float
    half_life_minutes: float
    busy_at: float
    low_at: float

    def measured(self, items: list[LoadItem], moment: float) -> AgentLoad:
        window = self.window_minutes * 60
        walk = self.walk(items, moment, window + HALF_LIVES * self.half_life_minutes * 60)
        series, arrivals, clearings, wait = list(walk.points), walk.arrivals, walk.clearings, walk.wait_minutes
        waiting = sum(item.weight for item in items if item.is_waiting(moment))
        rho = series[-1][1]
        sorted_waiting = sorted((item for item in items if item.is_waiting(moment)), key=lambda item: (item.arrived_at, item.ref))
        return AgentLoad(arrivals=round(arrivals, 2), clearings=round(clearings, 2), rho=round(rho, 2), waiting=round(waiting, 2), waiting_refs=tuple(item.ref for item in sorted_waiting[:WAITING_REFS_STORED]), waiting_items=len(sorted_waiting), oldest_wait_minutes=round(sum((moment - item.arrived_at) / 60 for item in sorted_waiting[:1]), 2),
                         wait_minutes=round(wait, 2), little=round(arrivals * wait / 60, 2), busy_minutes=self.stretch(series, lambda point: point[1] >= self.busy_at and point[2] > 0),
                         low_minutes=self.stretch(series, lambda point: point[1] < self.low_at), measured_at=moment)

    def walk(self, items: list[LoadItem], moment: float, horizon: float) -> QueueWalk:
        window = self.window_minutes * 60
        instants = [moment - horizon + step * STEP_SECONDS for step in range(int(horizon // STEP_SECONDS) + 1)]
        if instants[-1] < moment:
            instants.append(moment)
        half_life = HalfLife(self.half_life_minutes)
        arrivals = clearings = wait = None
        series: list[tuple[float, float, float]] = []
        for time in instants:
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
            series.append((time, arrivals / self.clearing_rate(clearings), waiting))
        return QueueWalk(tuple(series), arrivals, 0.0 if clearings is None else clearings, 0.0 if wait is None else wait)

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
            if finish <= reached:
                continue
            total += finish - max(begin, reached)
            reached = finish
        return total

    def least_clearings(self) -> float:
        return 60 / self.window_minutes

    def clearing_rate(self, clearings: float | None) -> float:
        return clearings if clearings is not None and clearings > 0 else self.least_clearings()

    @staticmethod
    def stretch(series: list[tuple[float, float, float]], condition) -> float:
        if not condition(series[-1]):
            return 0.0
        first_time = series[-1][0]
        for point in reversed(series):
            if not condition(point):
                break
            first_time = point[0]
        return round((series[-1][0] - first_time) / 60, 1)

