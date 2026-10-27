from dataclasses import dataclass


@dataclass(frozen=True)
class WorkerMention:
    """A worker as its events name it: its number, its name, the session that dispatched it and its own session."""

    id: int
    name: str
    dispatcher: str | None
    session: str = ""

    def ref(self) -> str:
        return f"workers:{self.id}"

    def label(self) -> str:
        return f"worker {self.id}"

    def title(self) -> str:
        return f"worker {self.id}, {self.name}"

    def is_other_dispatcher(self, session: str) -> bool:
        return self.dispatcher is not None and self.dispatcher != session
