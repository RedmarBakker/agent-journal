from dataclasses import dataclass


@dataclass(frozen=True)
class PastSession:
    """A conversation an agent program stored for this project on this machine, as the environment form lists it to carry on from: the program, its session id, when it was last written, its first prompt and how many lines its transcript holds."""

    provider: str
    session: str
    updated_at: float
    first_prompt: str
    line_count: int
