from dataclasses import dataclass, field


@dataclass(frozen=True)
class SupervisorReply:
    """What a supervisor answered a request: whether it did it, why not, to hello whether its code on disk changed since it started, and to memory the resident bytes of each process group it was handed."""

    success: bool
    error: str = ""
    outdated: bool = False
    groups: dict[int, int] = field(default_factory=dict)

    @classmethod
    def parsed(cls, data: dict) -> "SupervisorReply":
        return cls(bool(data.get("ok")), str(data.get("error", "")), bool(data.get("outdated")), {int(pid): int(size) for pid, size in data.get("groups", {}).items()})
