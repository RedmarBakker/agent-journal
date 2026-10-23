from dataclasses import dataclass

PROMPT_CHARACTERS = 70


@dataclass(frozen=True)
class PastSessionRow:
    """A conversation an agent program stored for the project, as the boot menu lists it to carry on from: its program and that program's title, its session, when it was last written, its first prompt, how many lines it holds, and the environment it already went into, if any."""

    provider: str
    session: str
    updated_at: float
    first_prompt: str
    line_count: int
    title: str
    environment: str

    @classmethod
    def parsed(cls, data: dict) -> "PastSessionRow":
        return cls(**data)

    def is_free(self) -> bool:
        return not self.environment

    def label(self) -> str:
        first_line = self.first_prompt.strip().split("\n", 1)[0]
        return first_line[:PROMPT_CHARACTERS] or "(no prompt of yours)"

    def badges(self) -> tuple[str, ...]:
        return self.title, f"{self.line_count} lines"
