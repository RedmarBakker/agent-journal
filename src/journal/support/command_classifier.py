import re

from journal.support.chain import Chain
from journal.support.classification import Classification
from journal.support.classification_table import ClassificationTable
from journal.support.part import Part
from journal.support.table_row import TableRow
from journal.support.writes import MARKERS

SUBSTITUTIONS = re.compile(r"\$\(([^()]*)\)|`([^`]*)`|<\(([^()]*)\)")
REDIRECT = re.compile(r"(&>>|&>|>>|>\||>)\s*(&?[^\s;&|]+)")
EXEC_FLAGS = frozenset({"-exec", "-execdir", "-ok"})
EXEC_ENDS = frozenset({";", "\\;", "+"})
SSH_VALUE_FLAGS = frozenset({"-p", "-i", "-o", "-l", "-F", "-J", "-L", "-R", "-D", "-W", "-b", "-c", "-E", "-m", "-O", "-Q", "-S", "-w"})
NETWORK = "reaches_network"
WRITES_FILES = "writes_files"


class CommandClassifier:
    """What a single shell command is and does, read from the shipped command table: its program's row with its subcommands and the modifiers of the options it carries, its wrappers taken off, its redirects and inner commands added; each line is classified once."""

    def __init__(self, table: ClassificationTable) -> None:
        self.table = table
        self.known: dict[str, Classification] = {}

    @property
    def version(self) -> int:
        return self.table.version

    def classify_line(self, line: str) -> Classification:
        return Classification.union(self.classify(part.text) for part in Chain.parts(line))

    def classify(self, text: str) -> Classification:
        if text not in self.known:
            self.known[text] = Classification.union([self.program_classification(text), *self.inner(text)])
        return self.known[text]

    def program_classification(self, text: str) -> Classification:
        tokens = self.table.unwrapped(Part(text).tokens())
        row = self.table.programs.get(tokens[0].rsplit("/", 1)[-1]) if tokens else None
        if row is None:
            return self.redirected(Classification(), text)
        rows = self.walked(row, tokens[1:])
        classification = Classification().with_row(next(level for level in reversed(rows) if level.kind or level is row))
        modifiers = {name: modifier for level in rows for name, modifier in level.modifiers.items()}
        for flag in (token for token in tokens[1:] if token.startswith("-")):
            classification = self.modified(classification, modifiers, flag)
        return self.interpreted(self.redirected(classification, text), text)

    def walked(self, row: TableRow, tokens: list[str]) -> list[TableRow]:
        rows, is_flag_value = [row], False
        for token in tokens:
            if is_flag_value or token in row.value_flags:
                is_flag_value = not is_flag_value and token in row.value_flags
                continue
            if token.startswith("-"):
                continue
            if token not in rows[-1].subcommands:
                break
            rows.append(rows[-1].subcommands[token])
        return rows

    def modified(self, classification: Classification, modifiers: dict[str, TableRow], flag: str) -> Classification:
        for name in self.flag_names(flag):
            classification = classification.with_row(modifiers[name]) if name in modifiers else classification
        return classification

    @staticmethod
    def flag_names(flag: str) -> list[str]:
        name = flag.split("=", 1)[0]
        if flag.startswith("--") or len(name) <= 2:
            return [name]
        return [name, *(f"-{letter}" for letter in name[1:])] if name[1:].isalpha() else [name, flag[:2]]

    def redirected(self, classification: Classification, text: str) -> Classification:
        writes = any(self.table.redirect_writes(operator, target) for operator, target in REDIRECT.findall(Part(text).unquoted()))
        return classification.with_effect(WRITES_FILES) if writes else classification

    @staticmethod
    def interpreted(classification: Classification, text: str) -> Classification:
        return classification.with_effect(WRITES_FILES) if classification.uncertain and classification.kind == "process" and MARKERS.search(text) else classification

    def inner(self, text: str) -> list[Classification]:
        substituted = [self.classify_line(next(group for group in groups if group)) for groups in SUBSTITUTIONS.findall(text) if any(groups)]
        tokens = self.table.unwrapped(Part(text).tokens())
        program = tokens[0].rsplit("/", 1)[-1] if tokens else ""
        lines = INNER_LINES.get(program, CommandClassifier.no_lines)(tokens[1:])
        return substituted + [self.classify_line(line) for line in lines if line]

    @staticmethod
    def no_lines(tokens: list[str]) -> list[str]:
        return []

    @staticmethod
    def script_lines(tokens: list[str]) -> list[str]:
        return tokens[tokens.index("-c") + 1:tokens.index("-c") + 2] if "-c" in tokens else []

    @staticmethod
    def joined_lines(tokens: list[str]) -> list[str]:
        return [" ".join(tokens)]

    @staticmethod
    def executed_lines(tokens: list[str]) -> list[str]:
        return [" ".join(CommandClassifier.executed(tokens[index + 1:])) for index, token in enumerate(tokens) if token in EXEC_FLAGS]

    @staticmethod
    def executed(tokens: list[str]) -> list[str]:
        return tokens[:next((position for position, token in enumerate(tokens) if token in EXEC_ENDS), len(tokens))]

    @staticmethod
    def remote_lines(tokens: list[str]) -> list[str]:
        position = 0
        while position < len(tokens) and tokens[position].startswith("-"):
            position += 2 if tokens[position] in SSH_VALUE_FLAGS else 1
        return [" ".join(tokens[position + 1:])]


# the programs that run a command line of their own, and how each hands it over: sh -c '<line>', eval <line>, find -exec <line> ;, ssh host '<line>'
INNER_LINES = {"sh": CommandClassifier.script_lines, "bash": CommandClassifier.script_lines, "zsh": CommandClassifier.script_lines, "eval": CommandClassifier.joined_lines,
               "find": CommandClassifier.executed_lines, "ssh": CommandClassifier.remote_lines}
