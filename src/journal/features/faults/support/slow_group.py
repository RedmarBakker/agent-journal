import re
from dataclasses import dataclass

from journal.models.timing import Timing


@dataclass(frozen=True)
class SlowGroup:
    """The logged requests of one route, a number in its path read as {n}: its name as METHOD route, how many were logged, the worst and the typical (the middle) time, and the timings themselves, the slowest first."""

    name: str
    timings: tuple[Timing, ...]

    @staticmethod
    def route_name(timing: Timing) -> str:
        return f"{timing.method} {re.sub(r'/\d+(?=/|$)', '/{n}', timing.route)}"

    @classmethod
    def grouped(cls, timings: list[Timing]) -> list["SlowGroup"]:
        route_timings: dict[str, list[Timing]] = {}
        for timing in timings:
            route_timings.setdefault(cls.route_name(timing), []).append(timing)
        groups = [cls(route, tuple(sorted(group_timings, key=lambda timing: -timing.ms))) for route, group_timings in route_timings.items()]
        return sorted(groups, key=lambda group: (-group.worst(), group.name))

    def worst(self) -> int:
        return self.timings[0].ms

    def typical(self) -> int:
        return self.timings[len(self.timings) // 2].ms

    def line(self) -> str:
        return f"{self.worst():>6} ms worst  {self.typical():>6} ms typical  {len(self.timings):>4} logged  {self.name}"
