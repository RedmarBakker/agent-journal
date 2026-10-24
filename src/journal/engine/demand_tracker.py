import threading
from dataclasses import replace

from journal.engine.demand import Demand
from journal.engine.demand_progress import DemandProgress
from journal.events.feature_data import FeatureData
from journal.support.moment import Moment


class DemandTracker:
    """Every agent's progress on the declared demands, by its session, kept in memory: at each of its tool uses each demand's requirement is read again, a new one starting at the moment before this tool use, a standing one keeping its start, and a met one cleared."""

    def __init__(self) -> None:
        self._progress: dict[str, dict[str, DemandProgress]] = {}
        self._lock = threading.Lock()

    def count(self, session: str, demands: tuple[Demand, ...], data: FeatureData, moment: Moment) -> None:
        with self._lock:
            tracked = self._progress.setdefault(session, {})
            for demand in demands:
                requirement, previous = demand.requirement(data), tracked.get(demand.key)
                start = previous.start if previous and previous.is_active() else replace(moment, tool_uses=moment.tool_uses - 1)
                tracked[demand.key] = DemandProgress(demand, requirement, start, moment) if requirement is not None else DemandProgress(demand)

    def progress(self, session: str) -> tuple[DemandProgress, ...]:
        with self._lock:
            return tuple(self._progress.get(session, {}).values())
