from dataclasses import dataclass, field


@dataclass(frozen=True)
class Turn:
    """One entry of an agent's conversation as the viewer's log shows it: who spoke, what kind it is, its text, the tools it used and what each call did, as its provider decoded it."""

    line: int
    speaker: str
    turn_type: str
    time: float
    text: str = ""
    tools: list[str] = field(default_factory=list)
    steps: list[dict] = field(default_factory=list)
