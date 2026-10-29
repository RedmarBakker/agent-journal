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

    def latest(self, prefixes: tuple[str, ...]) -> str:
        return next((word for word, _ in reversed(self.steps) if word.startswith(prefixes)), "")

    def added(self, word: str, time: float) -> "WorkerMoves":
        return WorkerMoves((*self.steps, (word, time)))

    def recent_count(self, word: str, boundary: str) -> int:
        boundary_index = max((i for i, (step_word, _) in enumerate(self.steps) if step_word == boundary), default=-1)
        return sum(1 for step_word, _ in self.steps[boundary_index + 1:] if step_word == word)

    def spans(self, openings: tuple[str, ...], closings: tuple[str, ...], end: float) -> list[tuple[float, float]]:
        spans, began = [], None
        for word, time in self.steps:
            if word in openings and began is None:
                began = time
            elif word in closings and began is not None:
                spans.append((began, time))
                began = None
        return [*spans, (began, end)] if began is not None else spans
