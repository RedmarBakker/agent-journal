import json
import re
from pathlib import Path

from journal.support.part import Part
from journal.support.table_row import TableRow
from journal.support.wrapper import Wrapper

TABLE = Path(__file__).with_name("command_table.json")
# the signs of the shell's own operators, which a word a wrapper hands on as its command never holds
OPERATOR_SIGNS = "<>|&;"


class ClassificationTable:
    """The shipped command table, read once into rows: each program with its subcommands and modifiers, the scripts it knows by their file name, the wrappers that run another command, and the redirects, each with the descriptor it moves and its target, and which of them write a file."""

    def __init__(self) -> None:
        data = json.loads(TABLE.read_text())
        self.version: int = data["version"]
        self.programs = {name: TableRow.parsed(data["programs"], name) for name in data["programs"]}
        self.wrappers = {name: Wrapper.parsed(data["wrappers"], name) for name in data["wrappers"]}
        self.scripts = [(re.compile(pattern), TableRow.parsed(data["scripts"], pattern)) for pattern in data["scripts"]]
        self.redirect_operators = frozenset(data["redirects"]["writes"])
        self.redirect_targets_kept = frozenset(data["redirects"]["except"])
        operators = sorted({*data["redirects"]["writes"], *data["redirects"]["reads"]}, key=len, reverse=True)
        self.redirection = re.compile(r"(\d*)(" + "|".join(map(re.escape, operators)) + r")\s*(&?[^\s;&|]+)")

    def redirect_writes(self, operator: str, target: str) -> bool:
        return operator in self.redirect_operators and target not in self.redirect_targets_kept and not target.startswith("&")

    def script(self, word: str) -> TableRow | None:
        return next((row for pattern, row in self.scripts if pattern.search(word)), None)

    def time_limit_removed(self, tokens: list[str]) -> list[str]:
        wrapper = self.wrappers.get(tokens[0].rsplit("/", 1)[-1]) if tokens else None
        return (wrapper.wrapped(tokens) if wrapper is not None and wrapper.limits_time else []) or tokens

    def shape_unwrapped(self, tokens: list[str]) -> list[str]:
        tokens = tokens[1:] if len(tokens) > 1 and "/" in tokens[0] and (follower := self.wrappers.get(tokens[1])) and follower.follows_scripts else tokens
        while tokens and (wrapper := self.wrappers.get(tokens[0].rsplit("/", 1)[-1])) and wrapper.shape_skipped and (inner := Part.leads(wrapper.wrapped(tokens))) and not any(sign in inner[0] for sign in OPERATOR_SIGNS):
            tokens = inner
        return tokens

    @staticmethod
    def is_program_word(word: str) -> bool:
        return not any(sign in word for sign in OPERATOR_SIGNS) and not word.startswith("$")

    def unwrapped(self, tokens: list[str]) -> list[str]:
        while tokens and (wrapper := self.wrappers.get(tokens[0].rsplit("/", 1)[-1])) and (inner := Part.leads(wrapper.wrapped(tokens))) and self.is_program_word(inner[0]):
            tokens = inner
        return tokens
