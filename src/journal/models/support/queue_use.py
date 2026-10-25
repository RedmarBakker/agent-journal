from dataclasses import dataclass


@dataclass(frozen=True)
class QueueUse:
    """How the orchestrator keeps its workers' queues, as last measured: the workers with a history of merges counted, those whose queue stood empty while tasks were open, and those whose queue held more than they drain in the hours the user set."""

    counted: int = 0
    empty: int = 0
    piling: int = 0

    @classmethod
    def parsed(cls, data: dict) -> "QueueUse":
        return cls(int(data["counted"]), int(data["empty"]), int(data["piling"]))

    def is_measured(self) -> bool:
        return self.counted > 0

    def steady_share(self) -> float:
        return (self.counted - self.empty - self.piling) / self.counted
