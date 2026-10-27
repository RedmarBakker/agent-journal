from dataclasses import dataclass, replace
from typing import Iterable

from journal.support.table_row import TableRow

UNKNOWN = "unknown"
# the journal's own commands, which write through its own funnels and never count as a write of the project; a build or an install makes files (makes_files) it names nowhere, which is no write either
JOURNAL = "journal"
# a chain is named by the kind of its weightiest part: a test run over the tee that keeps its log, an edit over a read, and a journal command or a program the table does not know over a read, so a line holding one is never only a read
KIND_ORDER = ("test run", "build", "package", "edit", "network", "version control", "check", "process", "journal", UNKNOWN, "search", "read")
WRITES = "writes_files"
FILE_CHANGING_EFFECTS = frozenset({WRITES, "deletes_files"})
# a program that runs code it is handed, whose writes the table cannot see
PROCESS = "process"
SEARCH = "search"
TEST_RUN = "test run"
BUILD = "build"
READ = "read"
READS = "reads_files"
# the kinds a command that only reads files is of: cat and ls, git log and git diff
VERSION_CONTROL = "version control"
READ_KINDS = frozenset({READ, VERSION_CONTROL})
READ_EFFECTS = frozenset({READS, "prints_files"})
# what a read may do beyond reading and still be shown as one: follow its file as it grows, as tail -f does, whatever the line leaves uncertain, as sqlite3 does
SHOWN_READ_EFFECTS = READ_EFFECTS | {"runs_long"}
# a commit, a merge or a pull, which waits for the merger's turn so no two change the branch at once
VERSION_CONTROL_CHANGE = "changes_version_control"


@dataclass(frozen=True)
class Classification:
    """What a shell command is and does, read from the command table: its kind, its effects, whether the line alone leaves its meaning uncertain, and the activity the table shows it as; a row that names a kind replaces the effects, one that names none adds to them."""

    command_type: str = UNKNOWN
    effects: tuple[str, ...] = ()
    uncertain: bool = False
    label: str = ""

    @classmethod
    def parsed(cls, data: dict) -> "Classification":
        return cls(command_type=data.get("command_type", data.get("kind", UNKNOWN)), effects=tuple(data.get("effects", ())), uncertain=bool(data.get("uncertain")), label=data.get("label", ""))

    @classmethod
    def union(cls, classifications: Iterable["Classification"]) -> "Classification":
        parts = list(classifications)
        if not parts:
            return cls()
        kind = min((part.command_type for part in parts), key=lambda kind: KIND_ORDER.index(kind) if kind in KIND_ORDER else len(KIND_ORDER))
        return cls(command_type=kind, effects=tuple(sorted({effect for part in parts for effect in part.effects})), uncertain=any(part.uncertain for part in parts), label=next((part.label for part in sorted(parts, key=lambda part: part.command_type != kind) if part.label), ""))

    def with_row(self, row: TableRow) -> "Classification":
        effects = row.effects if row.command_type else (*self.effects, *row.effects)
        return replace(self, command_type=row.command_type or self.command_type, effects=tuple(sorted(set(effects))), uncertain=self.uncertain or row.uncertain)

    def with_effect(self, effect: str) -> "Classification":
        return replace(self, effects=tuple(sorted({*self.effects, effect})))

    @property
    def is_read(self) -> bool:
        return not self.is_write and set(self.effects) <= READ_EFFECTS and self.is_read_kind

    @property
    def is_read_kind(self) -> bool:
        return set(self.effects) <= SHOWN_READ_EFFECTS and (self.is_search or self.command_type in READ_KINDS and READS in self.effects)

    @property
    def is_test_run(self) -> bool:
        return self.command_type == TEST_RUN

    @property
    def is_long_run(self) -> bool:
        return self.command_type in (TEST_RUN, BUILD)

    @property
    def is_search(self) -> bool:
        return self.command_type == SEARCH

    @property
    def is_harmless(self) -> bool:
        return self.command_type == READ and not self.effects

    @property
    def changes_version_control(self) -> bool:
        return VERSION_CONTROL_CHANGE in self.effects

    @property
    def is_writing_script(self) -> bool:
        return self.command_type == PROCESS and self.uncertain and WRITES in self.effects

    @property
    def is_write(self) -> bool:
        return self.command_type != JOURNAL and (bool(FILE_CHANGING_EFFECTS & set(self.effects)) or self.uncertain)
