from dataclasses import dataclass


@dataclass(frozen=True)
class WorkerEnd:
    """How a pool worker's run ended on the machine that ran it: what it printed or why it stopped, the conversation to resume, what it left in its worktree, and the files its commits touched."""

    outcome: str
    resume: str
    summary: str
    touched: tuple[str, ...] | None

    @classmethod
    def parsed(cls, body: dict) -> "WorkerEnd":
        return cls(body["outcome"], body["resume"], body["summary"], None if body["touched"] is None else tuple(body["touched"]))
