from dataclasses import dataclass, replace
from journal.support.alias_call import AliasCall
from pathlib import Path

from journal.support.chain import Chain
from journal.support.command_classifier import CommandClassifier
from journal.support.command_shape import CommandShape
from journal.support.command_part import CommandPart
from journal.support.operation import Operation
from journal.support.recorded_call import RecordedCall
from journal.support.writes import Writes


PANIC = "panic"

@dataclass(frozen=True)
class ToolCall:
    """The one reading of a tool call, made where the hook is translated and included on both tool events: the tool and its input as received, the operation its provider decoded, and what the operation does: the shell line and its parts, whether the call writes and which files it writes or reads, the skill it loads, and each part's classification with the table version it was read by."""

    tool: str
    input: dict
    operation: Operation
    command: str = ""
    parts: tuple[CommandPart, ...] = ()
    is_journal: bool = False
    writes: bool = False
    edited_paths: tuple[str, ...] = ()
    read_paths: tuple[str, ...] = ()
    file_lines: int = 0
    skill_loaded: str = ""
    work: str = ""
    table_version: int = 0

    @classmethod
    def decoded(cls, tool: str, input: dict, operation: Operation, parts: tuple[CommandPart, ...]) -> "ToolCall":
        command = operation.line()
        return cls(tool=tool, input=input, operation=operation, command=command, parts=parts, is_journal=bool(parts) and all(part.is_journal for part in parts), writes=operation.writes(),
                   edited_paths=operation.target_paths(), read_paths=operation.read_paths(), file_lines=operation.file_lines(), skill_loaded=operation.loaded_skill(), work=Chain.work(command) if command else "")

    def classified(self, classifier: CommandClassifier) -> "ToolCall":
        return replace(self, parts=tuple(replace(part, classification=classifier.classify(part.text)) for part in self.parts), table_version=classifier.version)

    def shell_lines(self) -> tuple[str, ...]:
        return (*(part.text for part in self.parts), self.command)

    def journal_text(self, noun: str) -> str:
        return " ".join(part.text for part in self.parts if part.journal_noun == noun)

    def is_journal_noun(self, noun: str) -> bool:
        return bool(self.parts) and all(part.journal_noun == noun for part in self.parts)

    def skill_folders(self, homes: tuple[str, ...], file_name: str) -> list[str]:
        folders = [Path(path).parent.name for path in self.read_paths if Path(path).name == file_name and any(f"{home}/" in path for home in homes)]
        return [name for name in dict.fromkeys([*folders, self.skill_loaded]) if name]

    @property
    def input_text(self) -> str:
        return " ".join(str(value) for value in self.input.values())

    def recorded(self) -> RecordedCall:
        return RecordedCall(command=self.command, parts=self.parts, writes=self.writes, edited_paths=self.edited_paths, read_paths=self.read_paths, work=self.work, shape=CommandShape.chain_shape(tuple(part.text for part in self.parts) or (self.command,)), operation=self.operation,
                            table_version=self.table_version)

    def as_data(self) -> dict:
        return self.recorded().as_data()

    def is_folder_write(self, root: Path, folder: Path) -> bool:
        return self.writes and any((root / Path(path).expanduser()).resolve().is_relative_to(folder) for path in self.edited_paths)

    def is_script(self) -> bool:
        return any(Writes.is_script(part.text) for part in self.parts)

    def is_panic_line(self) -> bool:
        return bool(self.parts) and all(AliasCall.parsed(part.text).name == PANIC for part in self.parts)

    def journal_parts(self) -> tuple[int, int]:
        commands = [part for part in self.parts if not part.is_folder_change]
        return sum(1 for part in commands if part.is_journal), len(commands)
