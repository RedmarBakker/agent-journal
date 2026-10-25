from dataclasses import dataclass
from datetime import datetime

from journal.support.chain import Chain

HOOK = "hook"
SHELL = "shell"


@dataclass(frozen=True)
class Bypass:
    """One hook or shell line that went around a journal that did not answer, as a line of runtime/bypass.log: when, which kind, and the agent or the line."""

    at: float
    kind: str
    subject: str

    @classmethod
    def parse(cls, line: str) -> "Bypass":
        at, kind, subject = line.split(" ", 2)
        return cls(float(at), kind, subject)

    def described(self) -> str:
        when = datetime.fromtimestamp(self.at).strftime("%H:%M:%S")
        if self.kind == SHELL:
            return f"{when} ran in the shell itself: {' && '.join(Chain.self_parts(self.subject))}"
        return f"{when} a hook of {self.subject} let the tool go on unchecked"
