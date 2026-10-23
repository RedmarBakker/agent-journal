from dataclasses import dataclass

PROMPT_CHARACTERS = 70


@dataclass(frozen=True)
class PastSessionRow:
    """A conversation an agent program kept for the project, as the boot menu lists it to carry on from: its program and that program's title, its session, when it was last written, its first prompt, how many lines it holds, and the environment it already went into, if any."""

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
        return self.first_prompt[:PROMPT_CHARACTERS] or "(no prompt)"

    def badges(self) -> tuple[str, ...]:
        return self.title, f"{self.line_count} lines"
