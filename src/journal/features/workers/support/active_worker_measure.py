from journal.models.worker import JOB_STARTS, MERGED, Worker
from journal.repositories.workers import Workers

RETURN_MOVES = (MERGED, "released", "retired", "stopped")


class ActiveWorkerMeasure:
    """The mean number of active workers in a window, weighted by time: a worker is active from its dispatch or its next job until its merge, its release, its retirement or its stop, so clocked out and waiting to be checked still counts."""

    def __init__(self, workers: Workers) -> None:
        self.workers = workers

    def mean(self, start: float, end: float) -> float:
        return sum(min(span_end, end) - max(span_start, start) for worker in self.workers.all() for span_start, span_end in worker.moves.spans(JOB_STARTS, RETURN_MOVES, end) if span_end > start and span_start < end) / (end - start)
