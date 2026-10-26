from dataclasses import dataclass

from journal.models.check import Check

TITLE_PREFIX = "the wait for "
TITLE_SUFFIX = " ends when this passes"
# the last lines of a passed check that the agent is shown
SHOWN_LINES = 5


@dataclass(frozen=True)
class PassedWait:
    """A check made for a wait the agent no longer holds, which passed: its number, what the wait was for, read from the check's title, and the last lines of its output."""

    check_id: int
    purpose: str
    lines: str

    @classmethod
    def read(cls, check: Check) -> "PassedWait":
        lines = "\n".join(check.last_output.strip().splitlines()[-SHOWN_LINES:]) or "the check passed"
        return cls(check.row_id, check.title.removeprefix(TITLE_PREFIX).removesuffix(TITLE_SUFFIX), lines)
