from journal.models.worker import JOB_STARTS, MERGED, Worker
from journal.repositories.tasks import Tasks
from journal.repositories.workers import Workers

IDLE_MOVES = ("reported", MERGED)
BUSY_MOVES = (*JOB_STARTS, "clocked in", "released", "retired", "stopped")


class FreePlaceMeasure:
    """The minutes in a window during which a free place and an open task outside any plan stood together, read from the workers' moves when asked: a worker's place is free from its report or its merge until its next job, its release, its retirement or its stop."""

    def __init__(self, workers: Workers, tasks: Tasks) -> None:
        self.workers, self.tasks = workers, tasks

    def minutes(self, start: float, end: float) -> float:
        if not self.tasks.unplanned_open_count():
            return 0.0
        return sum(min(idle_end, end) - max(idle_start, start) for worker in self.workers.all() for idle_start, idle_end in self.free_spans(worker, end) if idle_end > start and idle_start < end) / 60

    @staticmethod
    def free_spans(worker: Worker, end: float) -> list[tuple[float, float]]:
        spans, began = [], None
        for word, time in worker.moves.steps:
            if word in IDLE_MOVES and began is None:
                began = time
            elif word in BUSY_MOVES and began is not None:
                spans.append((began, time))
                began = None
        return [*spans, (began, end)] if began is not None else spans
