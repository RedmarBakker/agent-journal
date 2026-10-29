from dataclasses import dataclass
from typing import ClassVar


@dataclass(frozen=True)
class TypedLine:
    """A line typed into an agent's terminal, waiting for the prompt hook that proves it arrived; a piece of it the terminal broke off still proves it."""

    SPLIT_MARGIN: ClassVar[int] = 40

    environment_id: int
    line: str
    time: float
    tries: int = 1

    def matches_prompt(self, environment_id: int, prompt: str) -> bool:
        return self.environment_id == environment_id and self.contains(prompt)

    def contains(self, prompt: str) -> bool:
        text = " ".join(prompt.split())
        return self.line in text or (len(text) >= self.SPLIT_MARGIN and text in self.line)
