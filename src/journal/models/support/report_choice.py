from dataclasses import dataclass

from journal.support.rejection import Rejection

CHOICES = "each, queue or every <n> of two or more"


@dataclass(frozen=True)
class ReportChoice:
    """When a worker on a queue reports to its dispatcher: after each task (1), after every so many tasks, or once its queue is empty (0)."""

    tasks: int = 1

    @classmethod
    def parsed(cls, data: dict) -> "ReportChoice":
        return cls(int(data["tasks"]))

    @classmethod
    def argument(cls, values: list[str]) -> "ReportChoice":
        if values == ["each"]:
            return cls(1)
        if values == ["queue"]:
            return cls(0)
        if len(values) == 2 and values[0] == "every" and values[1].isdigit() and int(values[1]) >= 2:
            return cls(int(values[1]))
        raise Rejection(f"--report takes {CHOICES}, not '{' '.join(values)}'")

    def is_due(self, finished: int, queued: int) -> bool:
        if not queued:
            return True
        return bool(self.tasks) and finished + 1 >= self.tasks

    def label(self) -> str:
        if self.tasks == 1:
            return "each"
        return f"every {self.tasks}" if self.tasks else "queue"
