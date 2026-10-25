from dataclasses import dataclass, field


@dataclass
class OutputSilences:
    """For each output whose card is shown, how much it had printed when last looked at, when that last grew, and the longest it printed nothing while the run went on, kept in memory while the journal runs."""

    sizes: dict[int, int] = field(default_factory=dict)
    grown_at: dict[int, float] = field(default_factory=dict)
    longest: dict[int, float] = field(default_factory=dict)

    def sampled(self, output: int, size: int, started_at: float, time: float) -> None:
        if output not in self.sizes:
            self.sizes[output], self.grown_at[output] = size, time if size else started_at
        elif self.sizes[output] != size:
            self.sizes[output], self.grown_at[output] = size, time
        self.longest[output] = max(self.longest.get(output, 0.0), time - self.grown_at[output])

    def longest_seconds(self, output: int) -> float:
        return self.longest.get(output, 0.0)
