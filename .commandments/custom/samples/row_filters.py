class Board:
    """A sample for row-filter-outside-repository: the open tasks picked by a loop and the closed ones by a comprehension, where the repository should pick them; the third read asks the repository."""

    def __init__(self, tasks) -> None:
        self.tasks = tasks

    def open_titles(self) -> list[str]:
        titles = []
        # @sin RowFilterLoopOutsideRepositoryDetector
        for task in self.tasks.all():
            if task.is_open():
                titles.append(task.title)
        return titles

    def closed_titles(self) -> list[str]:
        # @sin RowFilterOutsideRepositoryDetector
        return [task.title for task in self.tasks.all() if task.is_closed()]

    def started_titles(self) -> list[str]:
        # @righteous RowFilterOutsideRepositoryDetector
        return [task.title for task in self.tasks.started()]
