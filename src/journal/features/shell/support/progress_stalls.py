from dataclasses import dataclass, field

from journal.support.timeout import Timeout


@dataclass
class ProgressStalls:
    """For each output whose card shows progress, the fraction it last showed, when that last changed, how many times it changed, and the longest it has stood still while the run went on, and when its progress last became complete, kept in memory while the journal runs."""

    fractions: dict[int, float] = field(default_factory=dict)
    moved_at: dict[int, float] = field(default_factory=dict)
    longest: dict[int, float] = field(default_factory=dict)
    changes: dict[int, int] = field(default_factory=dict)
    complete_at: dict[int, float] = field(default_factory=dict)

    def seen(self, output: int, fraction: float, time: float) -> None:
        if fraction >= 1.0:
            self.complete_at.setdefault(output, time)
        else:
            self.complete_at.pop(output, None)
        if not fraction or fraction >= 1.0:
            return
        if self.fractions.get(output) != fraction:
            self.fractions[output], self.moved_at[output] = fraction, time
            self.changes[output] = self.changes.get(output, 0) + 1
            return
        self.longest[output] = max(self.longest.get(output, 0.0), time - self.moved_at[output])

    def complete_seconds(self, output: int, time: float) -> float:
        return time - self.complete_at[output] if output in self.complete_at else 0.0

    def is_long_complete(self, output: int, wait: Timeout, time: float) -> bool:
        return output in self.complete_at and wait.started(self.complete_at[output]).is_elapsed(time)

    def longest_seconds(self, output: int) -> float:
        return self.longest.get(output, 0.0)

    def change_count(self, output: int) -> int:
        return self.changes.get(output, 0)

    def has_seen(self, output: int) -> bool:
        return output in self.fractions
