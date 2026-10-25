from dataclasses import dataclass


@dataclass(frozen=True)
class ProcessRow:
    """One process of the machine: its id, the id of the process that started it, and its command line."""

    pid: int
    parent: int
    command: str
