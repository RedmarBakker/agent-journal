from dataclasses import dataclass, field, replace
from types import MappingProxyType
from typing import Mapping

from journal.features.faults.support.route_cost import RouteCost
from journal.features.faults.support.slow_request_data import SlowRequestData
from journal.support.timeout import Timeout

GATHERED = 10
GAP_SECONDS = 30.0
SHOWN_ROUTES = 3


@dataclass(frozen=True)
class SlowRequestTally:
    """The requests over their points budget counted since the boot: each route's count and most points, how many gathered since the agent was last informed and the costliest of them, when the last arrived and when the agent was last informed."""

    routes: Mapping[str, RouteCost] = field(default_factory=lambda: MappingProxyType({}))
    gathered: int = 0
    costliest_route: str = ""
    worst_points: int = 0
    flagged_at: float = 0.0
    reported_at: float = 0.0

    def flagged(self, route: str, points: int, moment: float) -> "SlowRequestTally":
        routes = MappingProxyType({**self.routes, route: self.routes.get(route, RouteCost()).added(points)})
        costliest = (route, points) if points > self.worst_points else (self.costliest_route, self.worst_points)
        return replace(self, routes=routes, gathered=self.gathered + 1, costliest_route=costliest[0], worst_points=costliest[1], flagged_at=moment)

    def reported(self, moment: float) -> "SlowRequestTally":
        return replace(self, gathered=0, costliest_route="", worst_points=0, reported_at=moment)

    def is_gathered(self, moment: float) -> bool:
        return self.gathered >= GATHERED or (self.gathered > 0 and Timeout.seconds(GAP_SECONDS).started(self.flagged_at).is_elapsed(moment))

    def total(self) -> int:
        return sum(time.count for time in self.routes.values())

    def detail(self, budget: int) -> str:
        worst = sorted(self.routes.items(), key=lambda item: -item[1].worst_points)[:SHOWN_ROUTES]
        return f"{', '.join(time.label(route) for route, time in worst)}; budget {budget} points"

    def serialized(self) -> SlowRequestData:
        routes = {route: [time.count, time.worst_points] for route, time in self.routes.items()}
        return SlowRequestData(routes=routes, gathered=self.gathered, costliest_route=self.costliest_route, worst_points=self.worst_points, flagged_at=self.flagged_at, reported_at=self.reported_at)
