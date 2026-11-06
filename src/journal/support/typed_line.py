from dataclasses import dataclass
from typing import ClassVar

JOURNAL_PREFIX = "[journal]"


@dataclass(frozen=True)
class TypedLine:
    """A line typed into an agent's terminal, confirmed by a prompt containing its words with or without the journal marker; a broken-off piece of it also proves it arrived."""

    SPLIT_MARGIN: ClassVar[int] = 40

    environment_id: int
    line: str
    time: float
    tries: int = 1
    agent_id: int = 0

    def matches_prompt(self, environment_id: int, prompt: str, agent_id: int = 0) -> bool:
        return self.environment_id == environment_id and (not agent_id or self.agent_id in (0, agent_id)) and self.contains(prompt)

    def contains(self, prompt: str) -> bool:
        text = " ".join(prompt.split())
        line = self.line.removeprefix(f"{JOURNAL_PREFIX} ")
        return line in text or (len(text) >= self.SPLIT_MARGIN and text in self.line)
