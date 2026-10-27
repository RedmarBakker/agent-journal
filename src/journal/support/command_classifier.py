import re
import shlex
from dataclasses import replace

from journal.support.chain import Chain
from journal.support.classification import FILE_CHANGING_EFFECTS, Classification
from journal.support.classification_table import ClassificationTable
from journal.support.command_shape import LOOP_PATTERN, CommandShape
from journal.support.part import Part
from journal.support.table_row import TableRow

# a group of commands in braces, run as one
GROUP = re.compile(r"^\s*\{.*\}\s*$", re.S)
SUBSTITUTIONS = re.compile(r"\$\(([^()]*)\)|`([^`]*)`|<\(([^()]*)\)")
REDIRECT = re.compile(r"(&>>|&>|>>|>\||>)\s*(&?[^\s;&|]+)")
# a redirect with the descriptor it moves, which is no word the command is given
REDIRECTION = re.compile(r"(\d*)" + REDIRECT.pattern)
# the descriptors of a command's standard output: none written, or 1
OUTPUT_DESCRIPTORS = ("", "1")
EXEC_FLAGS = frozenset({"-exec", "-execdir", "-ok"})
EXEC_ENDS = frozenset({";", "\\;", "+"})
SSH_VALUE_FLAGS = frozenset({"-p", "-i", "-o", "-l", "-F", "-J", "-L", "-R", "-D", "-W", "-b", "-c", "-E", "-m", "-O", "-Q", "-S", "-w"})
NETWORK = "reaches_network"
# what code handed to an interpreter does when it writes a file, which no table row can tell
MARKERS = re.compile(r"write_text|write_bytes|open\([^)]*[\"'][wax]|\.write\(|unlink|os\.remove|shutil\.|os\.rename|\.rename\(|mkdir|writeFileSync|writeFile\(|fs\.write|File\.(write|open|delete)|rm_rf|\.truncate\(")
WRITES_FILES = "writes_files"
PRINTS_FILES = "prints_files"
# the kinds whose words name the files they write, as rm build, sed -i s/a/b/ notes.txt and git checkout -- a.py do; a build or an install makes files it does not name
NAMING_KINDS = frozenset({"edit", "version control"})
# a path written in quotes in code handed to an interpreter, which the code may write
QUOTED_PATH = re.compile(r"['\"]([^'\"\s]*/[^'\"\s]*)['\"]")


class CommandClassifier:
    """What a single shell command is and does, read from the shipped command table: each command of its pipe or its || by its program's row with its subcommands and the modifiers of the options it carries, its wrappers taken off, its redirects and inner commands added; each line is classified once."""

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
            self.known[text] = Classification.union(self.classify_command(piped) for piped in Part(text).commands())
        return self.known[text]

    def classify_command(self, text: str) -> Classification:
        if Part(text).is_subshell() or GROUP.match(text):
            return self.classify_line(text.strip()[1:-1])
        looped = [command for command in (CommandShape.inner(command) for command in CommandShape.commands(text)) if command] if LOOP_PATTERN.match(text) else [text]
        if looped != [text]:
            return self.redirected(Classification.union(self.classify(command) for command in looped), text)
        return Classification.union([self.program_classification(text), *self.inner(text)])

    def program_classification(self, text: str) -> Classification:
        tokens = self.tokens(text)
        row = self.row(tokens)
        return self.interpreted(self.redirected(self.row_classification(text), text), row, text) if row is not None else self.redirected(Classification(), text)

    def row_classification(self, text: str) -> Classification:
        tokens = self.tokens(text)
        row = self.row(tokens)
        if row is None:
            return Classification()
        rows, arguments = self.walked(row, tokens[1:])
        label = row.bare_label if len(rows) == 1 and not arguments and row.bare_label else next((level.label for level in reversed(rows) if level.label), "")
        classification = Classification(label=label).with_row(next(level for level in reversed(rows) if level.kind or level is row))
        modifiers = {name: modifier for level in rows for name, modifier in level.modifiers.items()}
        for flag in (token for token in tokens[1:] if token.startswith("-")):
            classification = self.modified(classification, modifiers, flag)
        return classification

    def unwrapped(self, text: str) -> str:
        tokens = Part(text).tokens()
        bare = self.table.unwrapped(tokens)
        return text if bare == tokens else shlex.join(bare)

    def time_unlimited(self, line: str) -> str:
        stages = Part(line).stages()
        tokens = Part(stages[0]).tokens()
        bare = self.table.time_limit_removed(tokens)
        return line if bare == tokens else " | ".join([shlex.join(bare), *stages[1:]])

    def process_command(self, command: str) -> str:
        tokens = self.table.unwrapped(command.split())
        row = self.table.programs.get(tokens[0].rsplit("/", 1)[-1]) if tokens else None
        if row is None or not row.starts_processes:
            return " ".join(tokens)
        return " ".join(tokens[tokens.index("-c") + 1:]).strip("'\"") if "-c" in tokens else ""

    def redirects_output(self, text: str) -> bool:
        return any(descriptor in OUTPUT_DESCRIPTORS for descriptor, operator, target in REDIRECTION.findall(Part(text).blanked()))

    def redirected_label(self, word: str) -> str:
        row = self.table.programs.get(word.rsplit("/", 1)[-1])
        return row.redirected_label if row is not None else ""

    def shell_script(self, line: str) -> str:
        tokens = self.tokens(line)
        reader = INNER_LINES.get(tokens[0].rsplit("/", 1)[-1]) if tokens else None
        return next(iter(reader(tokens[1:])), "") if reader == CommandClassifier.script_lines else ""

    def runs_script_file(self, word: str) -> bool:
        row = self.table.programs.get(word.rsplit("/", 1)[-1])
        return row is not None and row.runs_script_file

    def tokens(self, text: str) -> list[str]:
        return self.table.unwrapped(Part(text).tokens())

    def row(self, tokens: list[str]) -> TableRow | None:
        if not tokens:
            return None
        row = self.table.programs.get(tokens[0].rsplit("/", 1)[-1])
        script = next((token for token in tokens[1:] if not token.startswith("-")), "") if row is not None and row.interpreted else tokens[0]
        return self.table.script(script) or row

    def walked(self, row: TableRow, tokens: list[str]) -> tuple[list[TableRow], list[str]]:
        rows, arguments, is_flag_value = [row], [], False
        for token in tokens:
            if is_flag_value or token in row.value_flags:
                is_flag_value = not is_flag_value and token in row.value_flags
                continue
            if token.startswith("-") or "=" in token:
                continue
            subcommand_row = None if arguments else self.subcommand(rows[-1], token)
            if subcommand_row is None:
                arguments.append(token)
            else:
                rows.append(subcommand_row)
        return rows, arguments

    def target_paths(self, text: str) -> tuple[str, ...]:
        return tuple(path for piped in Part(text).commands() for path in [*self.redirect_targets(piped), *self.target_arguments(piped)] if path)

    def read_paths(self, text: str) -> tuple[str, ...]:
        return tuple(path for piped in Part(text).commands() if PRINTS_FILES in self.row_classification(piped).effects for path in self.arguments(piped))

    def stage_arguments(self, text: str) -> list[str]:
        return [word for piped in Part(text).commands() for word in self.arguments(piped)]

    def arguments(self, text: str) -> list[str]:
        tokens = self.tokens(REDIRECTION.sub(" ", Part(text.split("\n", 1)[0]).blanked()))
        row = self.row(tokens)
        return [word for word in self.walked(row, tokens[1:])[1] if word and not word.startswith(("<", "|"))] if row is not None else []

    def target_arguments(self, text: str) -> list[str]:
        program = self.row_classification(text)
        if program.is_write:
            return self.arguments(text) if program.kind in NAMING_KINDS and FILE_CHANGING_EFFECTS & set(program.effects) else []
        return [*QUOTED_PATH.findall(text), *(word for word in self.arguments(text) if "/" in word)] if self.runs_writing_code(text) else []

    def runs_writing_code(self, text: str) -> bool:
        row = self.row(self.tokens(text))
        return row is not None and row.interpreted and bool(MARKERS.search(text))

    @staticmethod
    def subcommand(row: TableRow, token: str) -> TableRow | None:
        return next((row.subcommands[word] for word in (token, token.strip("'\""), token.rsplit("/", 1)[-1], token.split(":")[0], token.split(" ")[0]) if word in row.subcommands), None)

    def modified(self, classification: Classification, modifiers: dict[str, TableRow], flag: str) -> Classification:
        for name in self.flag_names(flag):
            classification = replace(classification.with_row(modifiers[name]), label=modifiers[name].label or classification.label) if name in modifiers else classification
        return classification

    @staticmethod
    def flag_names(flag: str) -> list[str]:
        name = flag.split("=", 1)[0]
        if flag.startswith("--") or len(name) <= 2:
            return [name]
        return [name, *(f"-{letter}" for letter in name[1:] if letter.isalpha())] if name[1:].isalnum() else [name, flag[:2]]

    def redirected(self, classification: Classification, text: str) -> Classification:
        return classification.with_effect(WRITES_FILES) if self.redirect_targets(text) else classification

    def redirect_targets(self, text: str) -> list[str]:
        return [target.strip("'") for operator, target in REDIRECT.findall(Part(text).blanked()) if self.table.redirect_writes(operator, target)]

    @staticmethod
    def interpreted(classification: Classification, row: TableRow, text: str) -> Classification:
        return replace(classification.with_effect(WRITES_FILES), uncertain=True) if row.interpreted and MARKERS.search(text) else classification

    def inner(self, text: str) -> list[Classification]:
        substituted = [self.classify_line(next(group for group in groups if group)) for groups in SUBSTITUTIONS.findall(Part(text).unexpanded()) if any(groups)]
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
