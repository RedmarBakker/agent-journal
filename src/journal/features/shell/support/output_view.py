import re
from dataclasses import dataclass

from journal.chat.card_detail import CardDetail
from journal.models.message import Message

WATCH_KEY = "watch"
PROGRESS_FIGURE = re.compile(r"\d+/\d+|\d+%")


@dataclass(frozen=True)
class OutputView:
    """What a watch on an output shows: the lines its reader picks, or its last lines, how far its command has come, as words and as a fraction, how it ended once it has, whether its card has shown nothing for 30 seconds while it runs, whether it ended printing no summary, so its card ends on the counts of its step marks, whether its reader counts steps, and the command it runs, shortened."""

    output: int
    lines: tuple[str, ...]
    figure: str
    fraction: float
    ending: str
    reader: str = ""
    poor_line: str = ""
    empty_card: bool = False
    silent: bool = False
    summary_missing: bool = False
    is_counting: bool = False
    command: str = ""
    complete_unended: bool = False

    @classmethod
    def empty(cls) -> "OutputView":
        return cls(0, (), "", 0.0, "")

    @classmethod
    def unmeasured(cls, output: int, lines: tuple[str, ...], ending: str) -> "OutputView":
        return cls(output, lines, "", 0.0, ending)

    @classmethod
    def parsed(cls, card: Message) -> "OutputView":
        lines = card.data.get("lines") or [card.data["detail"]]
        return cls(card.data["output"], tuple(line for line in lines if line), card.data["figure"], card.data["fraction"], card.data["ending"], card.data.get("reader", ""), card.data.get("poor_line", ""), card.data.get("empty_card", False), card.data.get("silent", False), card.data.get("summary_missing", False), command=CardDetail.shortened(str(card.data.get("line", ""))), complete_unended=card.data.get("complete_unended", False))

    @staticmethod
    def key(output: int) -> str:
        return f"{WATCH_KEY}:{output}"

    def is_watching(self) -> bool:
        return self.output > 0

    def text(self) -> str:
        return "\n".join([line for line in (self.figure, *self.lines) if line]) or "no lines yet"

    def progress(self) -> str:
        counted = PROGRESS_FIGURE.search(self.figure)
        if counted:
            return counted.group(0)
        return f"{round(self.fraction * 100)}%" if self.fraction else "running"

    def outcome(self, ending: str) -> str:
        return "failed" if (self.ending or ending).startswith("failed") else "completed"
