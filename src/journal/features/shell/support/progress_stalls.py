from dataclasses import dataclass, field


@dataclass
class ProgressStalls:
    """For each output whose card shows progress, the fraction it last showed, when that last changed, how many times it changed, and the longest it has stood still while the run went on, kept in memory while the journal runs."""

    fractions: dict[int, float] = field(default_factory=dict)
    moved_at: dict[int, float] = field(default_factory=dict)
    longest: dict[int, float] = field(default_factory=dict)
    changes: dict[int, int] = field(default_factory=dict)

    def seen(self, output: int, fraction: float, time: float) -> None:
        if not fraction or fraction >= 1.0:
            return
        if self.fractions.get(output) != fraction:
            self.fractions[output], self.moved_at[output] = fraction, time
            self.changes[output] = self.changes.get(output, 0) + 1
            return
        self.longest[output] = max(self.longest.get(output, 0.0), time - self.moved_at[output])

    def longest_seconds(self, output: int) -> float:
        return self.longest.get(output, 0.0)

    def change_count(self, output: int) -> int:
        return self.changes.get(output, 0)

    def has_seen(self, output: int) -> bool:
        return output in self.fractions
