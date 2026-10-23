from dataclasses import dataclass


@dataclass(frozen=True)
class WorkerMoves:
    """The moves a worker made, each its word and its time, in the order it made them."""

    steps: tuple[tuple[str, float], ...] = ()

    @classmethod
    def parsed(cls, data: dict) -> "WorkerMoves":
        return cls(tuple((str(word), float(time)) for word, time in data["steps"]))

    def added(self, word: str, time: float) -> "WorkerMoves":
        return WorkerMoves((*self.steps, (word, time)))
