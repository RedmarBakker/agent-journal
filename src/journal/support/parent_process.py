import os
from dataclasses import dataclass


@dataclass(frozen=True)
class ParentProcess:
    """The process this one lives for, named by its starter in an environment variable, else this process's parent; a framework build's python starts the real interpreter as a child of its own, which outlives a killed parent, so the parent pid alone never changes."""

    pid: int

    @classmethod
    def named(cls, variable: str) -> "ParentProcess":
        return cls(int(os.environ.get(variable) or os.getppid()))

    def is_alive(self) -> bool:
        try:
            os.kill(self.pid, 0)
        except ProcessLookupError:
            return False
        except PermissionError:
            return True
        return True
