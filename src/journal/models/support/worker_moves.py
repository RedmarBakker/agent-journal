from dataclasses import dataclass


@dataclass(frozen=True)
class WorkerMoves:
    """The moves a worker made, each its word and its time, in the order it made them."""

    steps: tuple[tuple[str, float], ...] = ()

    @classmethod
    def parsed(cls, data: dict) -> "WorkerMoves":
        return cls(tuple((str(word), float(time)) for word, time in data["steps"]))

    def last_time(self) -> float:
        return self.steps[-1][1] if self.steps else 0.0

    def added(self, word: str, time: float) -> "WorkerMoves":
        return WorkerMoves((*self.steps, (word, time)))

    def counted_since(self, word: str, boundary: str) -> int:
        last = max((i for i, (each, _) in enumerate(self.steps) if each == boundary), default=-1)
        return sum(1 for each, _ in self.steps[last + 1:] if each == word)
