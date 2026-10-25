from collections.abc import Callable

STEPS = ("asking the plugins about its branch", "merging its branch", "closing its tasks", "moving its worktree up", "sending its next task")


class MergeSteps:
    """Where a worker's merge stands, told one numbered line per step as it starts, step 2/5 merging its branch, to whoever runs it, each followed by a line `now: ` that says what is happening at that moment, and the plugins' own statuses as they come: the command prints them, so a merge in the background shows its progress on its card; a merge from the viewer tells no one."""

    def __init__(self, writer: Callable[[str], None]) -> None:
        self.writer = writer

    @classmethod
    def silent(cls) -> "MergeSteps":
        return cls(lambda line: None)

    @staticmethod
    def sentence(number: int) -> str:
        return STEPS[number - 1]

    def started(self, number: int, detail: str = "", waiting: str = "") -> None:
        self.writer(f"step {number}/{len(STEPS)}: {self.sentence(number)}{detail}")
        self.status(waiting or self.sentence(number))

    def status(self, text: str) -> None:
        self.writer(f"now: {text}")
