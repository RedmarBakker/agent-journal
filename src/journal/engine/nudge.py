import re
from dataclasses import dataclass, field, replace

from journal.support.timeout import Timeout

NORMAL_LONGEST_CHARACTERS = 120
CUT_MARK = "…"
PLACEHOLDER = re.compile(r"\{\{(\w+)(?:\|cap=(\d+))?\}\}")


@dataclass(frozen=True)
class Nudge:
    """A line a feature can say to the agent, declared once: its name, its words as a template, and the feature that owns it, whose switch silences it. A value written {{name|cap=N}} is cut to N characters. A line longer than its longest, 120 unless it declares more with a reason, is cut to it when sent. It is not said again within its repeat span of the last time it was said, in seconds or tool uses. A remark asks for nothing now, so it is never typed to an idle agent: it waits for the agent's next hook."""

    feature: str
    name: str
    title: str
    brief: str = ""
    repeat: Timeout = Timeout.seconds(300)
    chat_answerable: bool = False
    blocks_regardless: bool = False
    is_remark: bool = False
    longest_characters: int = NORMAL_LONGEST_CHARACTERS
    longest_reason: str = ""
    values: dict = field(default_factory=dict)

    def create(self, **values) -> "Nudge":
        return replace(self, values=values)

    def rendered(self) -> str:
        title, brief = self._fill(self.title), self._fill(self.brief)
        if not brief:
            return title
        return f"{title} {brief}" if title.endswith(("?", "!", ".")) else f"{title}. {brief}"

    def is_too_long(self, line: str) -> bool:
        return len(line) > self.longest_characters

    def cut(self, line: str) -> str:
        return line if not self.is_too_long(line) else line[: self.longest_characters - len(CUT_MARK)] + CUT_MARK

    def _fill(self, template: str) -> str:
        return PLACEHOLDER.sub(self._value, template)

    def _value(self, placeholder: re.Match) -> str:
        value = str(self.values.get(placeholder.group(1), placeholder.group(0)))
        return self._capped(value, int(placeholder.group(2))) if placeholder.group(2) else value

    @staticmethod
    def _capped(value: str, cap: int) -> str:
        return value if len(value) <= cap else value[: cap - len(CUT_MARK)] + CUT_MARK

    @property
    def key(self) -> str:
        return f"{self.feature}.{self.name}"
