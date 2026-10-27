import re
from dataclasses import dataclass


@dataclass(frozen=True)
class StartingReader:
    """What a reader of one kind of run starts from before the run's own output fills it: the label its card shows, the pattern of its failure lines, of its summary line and of the other lines worth seeing, each kept only when the output holds such a line."""

    label: str
    failures: str = ""
    summary: str = ""
    notable: str = ""

    def failure_pattern(self, lines: list[str]) -> str:
        return self.found(self.failures, lines)

    def summary_pattern(self, lines: list[str]) -> str:
        return self.found(self.summary, lines)

    def picked(self, lines: list[str]) -> list[str]:
        return [pattern for pattern in (self.failure_pattern(lines), self.summary_pattern(lines), self.found(self.notable, lines)) if pattern]

    @staticmethod
    def found(pattern: str, lines: list[str]) -> str:
        return pattern if pattern and any(re.search(pattern, line) for line in lines) else ""
