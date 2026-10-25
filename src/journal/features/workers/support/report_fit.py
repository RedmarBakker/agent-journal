from journal.features.workers.support.task_sizes import TaskSizes
from journal.models.support.report_choice import ReportChoice
from journal.models.task import Task


class ReportFit:
    """The report choice that fits the work given to a worker better than its own, or none when its own fits: several small tasks fit reporting once the queue is empty, a long queue of large tasks fits reporting every two, and every n beyond the tasks given fits reporting at the queue's end."""

    def __init__(self, sizes: TaskSizes) -> None:
        self.sizes = sizes

    def better(self, choice: ReportChoice, tasks: list[Task]) -> ReportChoice | None:
        if choice.tasks == 1 and len(tasks) >= 2 and all(self.sizes.is_small(task) for task in tasks):
            return ReportChoice(0)
        if choice.tasks == 0 and self.sizes.is_long(tasks) and all(self.sizes.is_large(task) for task in tasks):
            return ReportChoice(2)
        if choice.tasks > 1 and choice.tasks > len(tasks):
            return ReportChoice(0)
        return None
