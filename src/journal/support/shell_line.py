from dataclasses import dataclass

from journal.support.operation import Operation


@dataclass(frozen=True)
class ShellLine(Operation):
    """A shell command the agent is about to run, as one line; whether it writes and the files it names are read from its parts' classification."""

    kind = "shell line"
    command: str

    def line(self) -> str:
        return self.command
