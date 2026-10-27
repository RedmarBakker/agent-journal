import shlex
from dataclasses import dataclass, field

from journal.support.alias_call import AliasCall
from journal.support.chain import Chain
from journal.support.command_shape import CommandShape
from journal.models.model import Model
from journal.support.part import Part

ARGS = "{args}"


@dataclass(frozen=True)
class Alias(Model):
    """A name for a command line of the project, run as journal <name> with its arguments passed on: the line, the reader that reads its output, what it does, the variables put before it, the plugin that shipped it, empty for one the agent or the user made, whether a run moves to the background the moment it starts, and whether a worker may run it, which a plugin declares of an alias that only reads."""

    name: str = ""
    line: str = ""
    reader: str = ""
    description: str = ""
    variables: dict = field(default_factory=dict)
    plugin: str = ""
    background: bool = False
    worker_access: bool = False

    def command(self, args: str) -> str:
        assignments = " ".join(f"{key}={shlex.quote(str(value))}" for key, value in self.variables.items())
        return f"{assignments} {self.expanded(args)}".strip()

    def expanded(self, args: str) -> str:
        return self.line.replace(ARGS, args) if ARGS in self.line else f"{self.line} {args}"

    def head_size(self) -> int:
        return len(Part(self.line.split(ARGS)[0]).tokens())

    def terminal_line(self, argv: list[str]) -> str:
        return self.command(" ".join(shlex.quote(word) for word in argv))

    def matches(self, part: str) -> bool:
        return self.starts(part) or " " in CommandShape.build(part) and CommandShape.build(part) == CommandShape.build(self.line)

    def starts(self, part: str) -> bool:
        head, tokens = Part(self.line.split(ARGS)[0]).tokens(), Part(part).tokens()
        return bool(head) and len(tokens) >= len(head) and tokens[0].rsplit("/", 1)[-1] == head[0].rsplit("/", 1)[-1] and tokens[1:len(head)] == head[1:]

    @staticmethod
    def resolved(line: str, index: "dict[str, Alias]") -> str:
        for part in Chain.parts(line):
            call = AliasCall.parsed(part.uncut().text)
            if part.recorded and call.name in index:
                line = Chain.replaced(line, part.text, f"{index[call.name].command(call.args)} {part.cut()}".strip())
        return line
