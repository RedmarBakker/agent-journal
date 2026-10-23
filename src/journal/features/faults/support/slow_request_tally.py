from dataclasses import dataclass, field, replace
from types import MappingProxyType
from typing import Mapping

from journal.features.faults.support.route_time import RouteTime
from journal.features.faults.support.slow_request_data import SlowRequestData
from journal.support.timeout import Timeout

GATHERED = 10
GAP_SECONDS = 30.0
SHOWN_ROUTES = 3


@dataclass(frozen=True)
class SlowRequestTally:
    """The slow requests one chat mark holds: each route's count and worst time, how many gathered since the agent was last informed and the slowest of them, when the last arrived and when the agent was last informed."""

    routes: Mapping[str, RouteTime] = field(default_factory=lambda: MappingProxyType({}))
    gathered: int = 0
    slowest_route: str = ""
    slowest_ms: int = 0
    flagged_at: float = 0.0
    reported_at: float = 0.0

    @classmethod
    def parsed(cls, data: SlowRequestData) -> "SlowRequestTally":
        routes = {route: RouteTime(count, worst_ms) for route, (count, worst_ms) in data["routes"].items()}
        return cls(MappingProxyType(routes), data["gathered"], data["slowest_route"], data["slowest_ms"], data["flagged_at"], data["reported_at"])

    def flagged(self, route: str, ms: int, moment: float) -> "SlowRequestTally":
        routes = MappingProxyType({**self.routes, route: self.routes.get(route, RouteTime()).added(ms)})
        slowest = (route, ms) if ms > self.slowest_ms else (self.slowest_route, self.slowest_ms)
        return replace(self, routes=routes, gathered=self.gathered + 1, slowest_route=slowest[0], slowest_ms=slowest[1], flagged_at=moment)

    def reported(self, moment: float) -> "SlowRequestTally":
        return replace(self, gathered=0, slowest_route="", slowest_ms=0, reported_at=moment)

    def is_gathered(self, moment: float) -> bool:
        return self.gathered >= GATHERED or (self.gathered > 0 and Timeout.seconds(GAP_SECONDS).started(self.flagged_at).is_elapsed(moment))

    def total(self) -> int:
        return sum(time.count for time in self.routes.values())

    def detail(self, budget: int) -> str:
        worst = sorted(self.routes.items(), key=lambda item: -item[1].worst_ms)[:SHOWN_ROUTES]
        return f"{', '.join(time.label(route) for route, time in worst)}; budget {budget} ms"

    def serialized(self) -> SlowRequestData:
        routes = {route: [time.count, time.worst_ms] for route, time in self.routes.items()}
        return SlowRequestData(routes=routes, gathered=self.gathered, slowest_route=self.slowest_route, slowest_ms=self.slowest_ms, flagged_at=self.flagged_at, reported_at=self.reported_at)
