from dataclasses import dataclass

from journal.models.worker import Worker


@dataclass(frozen=True)
class MergeCheck:
    """Whether the whole suite has passed since the latest merges: the workers merged since its last passing run, oldest first, and the output of its newest run that failed after the first of them, 0 when none has."""

    merged: tuple[Worker, ...] = ()
    failed_run: int = 0

    def workers_line(self) -> str:
        return ", ".join(f"worker {worker.id}, {worker.name} (task {worker.merged_task})" for worker in self.merged)
