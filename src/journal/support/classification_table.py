import json
import re
from pathlib import Path

from journal.config import Config
from journal.support.part import Part
from journal.support.table_row import TableRow
from journal.support.table_schema import TableSchema
from journal.support.wrapper import Wrapper

TABLE = Path(__file__).with_name("command_table.json")
# the project's own table for its own tools, in its journal's folder, merged over the shipped one
PROJECT_TABLE = "command_table.json"
# the sections of a project's table whose rows are put over the shipped ones, a row of the same name replacing the shipped row
PROJECT_SECTIONS = ("programs", "wrappers", "scripts")
# the signs of the shell's own operators, which a word a wrapper hands on as its command never holds
OPERATOR_SIGNS = "<>|&;"


class ClassificationTable:
    """The shipped command table with the project's own table for its own tools merged over it, read once into rows: each program with its subcommands and modifiers, the scripts it knows by their file name, the wrappers that run another command, and the redirects, each with the descriptor it moves and its target, and which of them write a file. A project's table that does not follow the schema is left out, its faults kept; the version is the shipped table's, so every journal of a release stamps the same one."""

    def __init__(self, config: Config, schema: TableSchema) -> None:
        shipped = json.loads(TABLE.read_text())
        merged = self.merged(shipped, config.home / PROJECT_TABLE)
        self.faults = schema.faults(merged) if merged is not shipped else []
        data = shipped if self.faults else merged
        self.version: int = data["version"]
        self.programs = {name: TableRow.parsed(data["programs"], name) for name in data["programs"]}
        self.wrappers = {name: Wrapper.parsed(data["wrappers"], name) for name in data["wrappers"]}
        self.scripts = [(re.compile(pattern), TableRow.parsed(data["scripts"], pattern)) for pattern in data["scripts"]]
        self.redirect_operators = frozenset(data["redirects"]["writes"])
        self.redirect_targets_kept = frozenset(data["redirects"]["except"])
        operators = sorted({*data["redirects"]["writes"], *data["redirects"]["reads"]}, key=len, reverse=True)
        self.redirection = re.compile(r"(\d*)(" + "|".join(map(re.escape, operators)) + r")\s*(&?[^\s;&|]+)")

    @staticmethod
    def merged(shipped: dict, project: Path) -> dict:
        if not project.is_file():
            return shipped
        project_table = json.loads(project.read_text())
        return {**shipped, **{section: {**shipped[section], **project_table.get(section, {})} for section in PROJECT_SECTIONS}}

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
