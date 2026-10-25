import re
from dataclasses import dataclass

from journal.features.shell.support.reader import Reader
from journal.features.shell.support.shell_runner import EXIT

# a run's summary line, as pytest and most runners print one at the end: how many passed, failed or erred
SUMMARY_LINE = re.compile(r"\b\d+ (?:passed|failed|errors?)\b")
FAILED_COUNT = re.compile(r"\b(\d+) (?:failed|errors?)\b")


@dataclass(frozen=True)
class TestRunResult:
    """How a worker's test run ended: its exit status and how many of its tests failed, counted on its last summary line, else by the step symbols the project's reader for its command counts, and at least one for a run that failed and names no count."""

    __test__ = False

    status: int
    failed: int

    @classmethod
    def read(cls, status: int, lines: list[str], reader: Reader | None) -> "TestRunResult":
        summary = next((line for line in reversed(lines) if SUMMARY_LINE.search(line)), "")
        named = sum(int(count) for count in FAILED_COUNT.findall(summary))
        tally = reader.tally(lines) if reader is not None else None
        counted = named or (tally.failed if tally is not None and tally.is_known() else 0)
        return cls(status, max(counted, 1) if status else counted)

    @classmethod
    def printed(cls, text: str, reader: Reader | None) -> "TestRunResult":
        lines = text.splitlines()
        ends = [line for line in lines if line.startswith(EXIT)]
        status = int(ends[-1].split()[-1]) if ends else 0
        return cls.read(status, [line for line in lines if not line.startswith(EXIT)], reader)

    def is_passed(self) -> bool:
        return not self.failed
