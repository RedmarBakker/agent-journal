from dataclasses import dataclass, field

from journal.support.process_usage import ProcessUsage
from journal.support.supervisor_process import SupervisorProcess


@dataclass(frozen=True)
class SupervisorReply:
    """What a supervisor answered a request: whether it did it, why not, to hello whether its code on disk changed since it started, to memory the resident bytes of each process group it was handed, to list the processes it runs, and to usage what each process group asked about takes of the machine."""

    success: bool
    error: str = ""
    outdated: bool = False
    groups: dict[int, int] = field(default_factory=dict)
    processes: tuple[SupervisorProcess, ...] = ()
    usage: dict[int, ProcessUsage] = field(default_factory=dict)

    @classmethod
    def parsed(cls, data: dict) -> "SupervisorReply":
        return cls(
            bool(data.get("ok")),
            str(data.get("error", "")),
            bool(data.get("outdated")),
            groups={int(pid): int(size) for pid, size in data.get("groups", {}).items()},
            processes=tuple(SupervisorProcess.parsed(process) for process in data.get("processes", [])),
            usage={int(group): ProcessUsage.parsed(fields) for group, fields in data.get("usage", {}).items()},
        )
