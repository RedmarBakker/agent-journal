from dataclasses import dataclass

KILOBYTE = 1024


@dataclass(frozen=True)
class ModelLoad:
    """How many rows of one model a request turned into models, how many bytes they held and how many writes it made to the model's table."""

    model: str
    rows: int
    bytes: int = 0
    writes: int = 0

    def points(self) -> int:
        return self.rows + self.writes + -(-self.bytes // KILOBYTE)
