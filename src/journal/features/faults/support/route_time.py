from dataclasses import dataclass


@dataclass(frozen=True)
class RouteTime:
    """How often one route went over its budget and its worst time."""

    count: int = 0
    worst_ms: int = 0

    def added(self, ms: int) -> "RouteTime":
        return RouteTime(self.count + 1, max(ms, self.worst_ms))

    def label(self, route: str) -> str:
        return f"{route} worst {self.worst_ms} ms, {self.count} {'time' if self.count == 1 else 'times'}"
