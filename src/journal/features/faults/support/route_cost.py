from dataclasses import dataclass


@dataclass(frozen=True)
class RouteCost:
    """How often one route went over its points budget and the most points one answer of it spent."""

    count: int = 0
    worst_points: int = 0

    def added(self, points: int) -> "RouteCost":
        return RouteCost(self.count + 1, max(points, self.worst_points))

    def label(self, route: str) -> str:
        return f"{route} worst {self.worst_points} points, {self.count} {'time' if self.count == 1 else 'times'}"
