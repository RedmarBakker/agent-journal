import re
from dataclasses import dataclass

from journal.support.chain import Chain
from journal.support.command_shape import CommandShape

COMMANDS_PREFIX = "commands: "
# a part whose standard output goes to a file, or that only asks the program its version or its help, shows no run of it on a card
OUTPUT_TO_FILE = re.compile(r"(?:^|\s)[1&]?>>?\s*\S+")
NO_RUN_FLAGS = ("--version", "--help", "-h", "-V")


@dataclass(frozen=True)
class ReaderCommands:
    """The commands a reader reads the output of, such as pytest or dotnet test: a shell line runs one when the shape of one of its parts, its program and subcommands, names it, never a value passed or text a part contains."""

    programs: tuple[str, ...] = ()

    @classmethod
    def parsed(cls, text: str) -> "ReaderCommands":
        return cls(tuple(word.strip() for word in text.split(",") if word.strip()))

    def text(self) -> str:
        return ", ".join(self.programs)

    def is_read(self, line: str) -> bool:
        return bool(self.read_part(line))

    def read_part(self, line: str) -> str:
        return next((part.text for part in Chain.parts(line) if self.reads(part.text)), "")

    def reads(self, part: str) -> bool:
        return any(re.search(rf"(^|[\s/]){re.escape(program)}(\s|$)", CommandShape.build(part)) for program in self.programs)

    def is_shown_run(self, line: str) -> bool:
        part = self.read_part(line)
        return bool(part) and not OUTPUT_TO_FILE.search(part) and not any(flag in part.split() for flag in NO_RUN_FLAGS)
