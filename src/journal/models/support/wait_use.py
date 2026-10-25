from dataclasses import dataclass


@dataclass(frozen=True)
class WaitUse:
    """How the tasks of the started plans wait, as last measured: the blocked or paused ones that wait with --on or --until, those with only a reason in words, those whose words name the user or an outside party with no command to check, the tasks that name another open task they do not wait on, each as task:other, and the started plans with many open tasks and none blocked."""

    with_wait: int = 0
    worded: int = 0
    outside: int = 0
    missing: tuple[str, ...] = ()
    unordered: int = 0

    @classmethod
    def parsed(cls, data: dict) -> "WaitUse":
        return cls(int(data["with_wait"]), int(data["worded"]), int(data["outside"]), tuple(data["missing"]), int(data["unordered"]))

    def scored(self) -> tuple[int, int]:
        return self.with_wait, self.with_wait + self.worded + len(self.missing) + self.unordered
