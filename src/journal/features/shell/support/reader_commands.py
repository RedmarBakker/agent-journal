import re
from dataclasses import dataclass


COMMANDS_PREFIX = "commands: "
JOURNAL = "journal"


@dataclass(frozen=True)
class ReaderCommands:
    """The commands a reader reads the output of, such as pytest or dotnet test: a part runs one when its shape, its program and subcommands, names it, never a value passed or text a part contains."""

    programs: tuple[str, ...] = ()

    @classmethod
    def parsed(cls, text: str) -> "ReaderCommands":
        return cls(tuple(word.strip() for word in text.split(",") if word.strip()))

    def text(self) -> str:
        return ", ".join(self.programs)

    def journal_commands(self) -> list[str]:
        return [" ".join(program.split()[1:2]) for program in self.programs if program.split()[:1] == [JOURNAL]]

    def reads(self, shape: str) -> bool:
        return any(re.search(rf"(^|[\s/]){re.escape(program)}(\s|$)", shape) for program in self.programs)
