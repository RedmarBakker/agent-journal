import shlex
from dataclasses import dataclass

from journal.support.operation import Operation


@dataclass(frozen=True)
class ShellLine(Operation):
    """A shell command the agent is about to run, as one line, with the shell and the flag it was handed to when the agent named them, as Codex does with bash -lc; whether it writes and the files it names are read from its parts' classification."""

    kind = "shell line"
    command: str
    shell: str = ""
    flag: str = ""

    def line(self) -> str:
        return self.command

    def shell_program(self) -> str:
        return self.shell

    def line_with_shell(self) -> str:
        return shlex.join([self.shell, self.flag, self.command]) if self.shell else self.command
