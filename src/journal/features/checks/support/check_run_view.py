from dataclasses import asdict, dataclass

from journal.models.check import Check
from journal.support.card_outcome import CardOutcome
from journal.support.check_progress import CheckProgress

CARD_LINES = 6


@dataclass(frozen=True)
class CheckRunView:
    """What a check run's card shows now: the last lines it printed, its count of a total and fraction for the bar, whether it counts, how it ended, its outcome and, once it ended, when."""

    lines: list[str]
    count: str
    fraction: float
    counting: bool
    ending: str
    outcome: str
    ended_at: float

    @classmethod
    def running(cls, progress: CheckProgress) -> "CheckRunView":
        count = f"{progress.finished_count}/{progress.total}" if progress.total else ""
        return cls(progress.output.splitlines()[-CARD_LINES:], count, (progress.percent or 0) / 100, progress.total > 0 or progress.percent is not None, "", str(CardOutcome.RUNNING), 0.0)

    @classmethod
    def ended(cls, check: Check, run_start: float) -> "CheckRunView":
        outcome = {True: CardOutcome.PASSED, False: CardOutcome.FAILED, None: CardOutcome.NONE}[check.last_passed]
        return cls(check.last_output.splitlines()[-CARD_LINES:], "", 0.0, False, check.verdict(), str(outcome), run_start + check.last_duration)

    def fields(self) -> dict:
        return asdict(self)
