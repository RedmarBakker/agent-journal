import json
from pathlib import Path

from journal.support.part import Part
from journal.support.table_row import TableRow
from journal.support.wrapper import Wrapper

TABLE = Path(__file__).with_name("command_table.json")


class ClassificationTable:
    """The shipped command table, read once into rows: each program with its subcommands and modifiers, the wrappers that run another command, and which redirects write a file."""

    def __init__(self) -> None:
        data = json.loads(TABLE.read_text())
        self.version: int = data["version"]
        self.programs = {name: TableRow.parsed(data["programs"], name) for name in data["programs"]}
        self.wrappers = {name: Wrapper.parsed(data["wrappers"], name) for name in data["wrappers"]}
        self.redirect_operators = frozenset(data["redirects"]["writes"])
        self.redirect_targets_kept = frozenset(data["redirects"]["except"])

    def redirect_writes(self, operator: str, target: str) -> bool:
        return operator in self.redirect_operators and target not in self.redirect_targets_kept and not target.startswith("&")

    def unwrapped(self, tokens: list[str]) -> list[str]:
        while tokens and (wrapper := self.wrappers.get(tokens[0].rsplit("/", 1)[-1])) and wrapper.is_wrapping(tokens):
            tokens = Part.leads(wrapper.wrapped(tokens))
        return tokens
