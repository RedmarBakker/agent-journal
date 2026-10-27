from datetime import datetime, timezone
from pathlib import Path
from journal.config import Config
from journal.models.alias import Alias
from journal.repositories.aliases import Aliases
from journal.support.chain import Chain
from journal.support.command_shape import CommandShape
from journal.features.shell.support.reader import Reader
from journal.features.shell.support.reader_commands import COMMANDS_PREFIX, JOURNAL, ReaderCommands
from journal.features.shell.support.output_files import OutputFiles
from journal.models.command_output import CommandOutput
from journal.support.actor import Actor
from journal.support.rejection import Rejection
from journal.features.plugins.support.plugin_skills import STAMP

# the readers chosen as their commands' defaults, one name a line, beside the readers
DEFAULTS_FILE = "defaults"
# the version of the rules the project's readers were written under, beside the readers; a new version clears the readers the project wrote
RULES_VERSION_FILE = "rules-version"
RULES_VERSION = 2

KINDS = (".pattern", ".sh")
# the readers the journal ships for a journal command that goes to the background, the one kind of reader of a journal command's output
JOURNAL_COMMAND_READERS = ("worker-merge",)
# the readers the journal ships: locked, never edited, removed or replaced by the agent or the user
SHIPPED_READERS = ("pytest", "vitest", "dotnet-test", "phpunit", "worker-merge")

# commands that only wait or print, which choose a line's reader only when no other part does work
IDLE_COMMANDS = {"sleep", "echo", "printf", "wait"}


class Readers:
    """The readers the project keeps in .journal/readers/, one file each, read by name; of several readers of one command the default reads it: the one the user chose, else the first made; one is removed with its files, never one a plugin ships; none reads a journal command's own output, an alias's run of a program aside."""

    def __init__(self, config: Config, aliases: Aliases, shapes: CommandShape) -> None:
        self.shapes = shapes
        self.config, self.aliases = config, aliases
        self.loaded: tuple[tuple, list[Reader]] = ((), [])

    def all(self) -> list[Reader]:
        if not self.config.readers.is_dir():
            return []
        paths = [path for path in sorted(self.config.readers.iterdir()) if path.suffix in KINDS]
        stamp = tuple((path.name, path.stat().st_mtime_ns) for path in paths)
        if stamp != self.loaded[0]:
            self.loaded = (stamp, [Reader.loaded(path) for path in paths])
        return self.loaded[1]

    def files(self, name: str) -> list[Path]:
        return [path for suffix in KINDS if (path := self.config.readers / f"{name}{suffix}").is_file()]

    def definition(self, name: str) -> str:
        return "\n".join(path.read_text() for path in self.files(name))

    def lookup(self, name: str) -> Reader:
        rows = self.files(name)
        if not rows:
            raise Rejection(f"no reader named {name}: `journal reader list` names them")
        return Reader.loaded(rows[0])

    def found(self, name: str) -> Reader | None:
        return Reader.loaded(self.files(name)[0]) if name and self.files(name) else None

    def revisions(self) -> dict[str, datetime]:
        return {reader.name: datetime.fromtimestamp(self.file_stamp(reader.name), timezone.utc) for reader in self.all()}

    def file_stamp(self, name: str) -> float:
        return max((path.stat().st_mtime for path in self.files(name)), default=0.0)

    def reading_output(self, name: str, output: CommandOutput) -> Reader:
        reader = self.lookup(name)
        if reader.commands.programs and not any(self.read_part(reader, line) for line in self.run_lines(output)):
            raise Rejection(f"the reader {name} reads {reader.commands.text()}, and output {output.id} is {output.headline()}: check the output's number with journal output list")
        return reader

    def run_lines(self, output: CommandOutput) -> list[str]:
        files = OutputFiles(Path(output.folder))
        commands = [output.command, *(files.part_text(i) for i in files.recorded())] if files.is_stored() else [output.command]
        return [*commands, *self.alias_lines(commands)]

    def alias_lines(self, commands: list[str]) -> list[str]:
        index = self.aliases.index()
        names = [segment.text.split()[1] for command in commands for segment in Chain.parts(command) if segment.text.split()[:1] == [JOURNAL] and len(segment.text.split()) > 1]
        return [index[name].line for name in names if name in index]

    def reading(self, line: str) -> Reader | None:
        readers = self.all()
        line_readers = next((matched for part in self.choosing_parts(line) if (matched := [reader for reader in readers if self.reads(reader, part)])), [])
        default_names = self.default_names()
        return next((reader for reader in line_readers if reader.name in default_names), None) or min(line_readers, key=self.creation_seconds, default=None)

    def choosing_parts(self, line: str) -> list[str]:
        commands = [segment for part in Chain.parts(line) if part.recorded for segment in Chain.commands(part.text)]
        with_programs = [(segment, shape) for segment in commands if (shape := self.shapes.build(segment))]
        working = [text for text, program in with_programs if not CommandShape.is_setup(program) and program.split()[0] not in IDLE_COMMANDS]
        return working or [text for text, _ in with_programs]

    def reads(self, reader: Reader, part: str) -> bool:
        return reader.commands.reads(self.shapes.build(part))

    def read_parts(self, reader: Reader, files: OutputFiles) -> list[int]:
        return [i for i, text in files.recorded_texts() if self.reads(reader, text)]

    def read_part(self, reader: Reader, line: str) -> str:
        return next((part.text for part in Chain.parts(line) if self.reads(reader, part.text)), "")

    def is_locked(self, name: str) -> bool:
        return name in SHIPPED_READERS or bool(self.owner(name))

    def refuse_locked(self, name: str, does: str) -> None:
        owner = self.owner(name)
        if owner:
            raise Rejection(f"the reader {name} is the plugin {owner}'s and locked: it is never {does}, and goes when the plugin is removed")
        if name in SHIPPED_READERS:
            raise Rejection(f"the reader {name} ships with the journal and is locked: it is never {does}")

    def removed(self, name: str) -> None:
        paths = self.files(name)
        if not paths:
            raise Rejection(f"no reader named {name}: `journal reader list` names them")
        self.refuse_locked(name, "removed")
        for path in paths:
            path.unlink()
        remaining = self.default_names() - {name}
        (self.config.readers / DEFAULTS_FILE).write_text("".join(f"{default}\n" for default in sorted(remaining)))

    def removed_with_aliases(self, name: str, actor: Actor) -> list[Alias]:
        self.removed(name)
        return [self.aliases.save(alias.with_(reader=""), actor) for alias in self.aliases.reader_rows(name)]

    def project_readers(self) -> list[Reader]:
        return [reader for reader in self.all() if not self.is_locked(reader.name)]

    def rules_version(self) -> int:
        path = self.config.readers / RULES_VERSION_FILE
        return int(path.read_text()) if path.is_file() else 0

    def rules_updated(self, actor: Actor) -> list[str]:
        cleared = [reader.name for reader in self.project_readers()]
        for name in cleared:
            self.removed_with_aliases(name, actor)
        self.config.readers.mkdir(parents=True, exist_ok=True)
        (self.config.readers / DEFAULTS_FILE).unlink(missing_ok=True)
        (self.config.readers / RULES_VERSION_FILE).write_text(f"{RULES_VERSION}\n")
        return cleared

    def owner(self, name: str) -> str:
        return next((line.removeprefix(STAMP) for path in self.files(name) for line in path.read_text().splitlines() if line.startswith(STAMP)), "")

    def journal_readers(self) -> list[Reader]:
        return [reader for reader in self.all() if self.reads_journal_output(reader) and not self.owner(reader.name)]

    def plugin_aliases_read(self, reader: Reader) -> list[Alias]:
        plugin_aliases = self.aliases.plugin_aliases()
        return [alias for alias in plugin_aliases if self.reads(reader, alias.expanded(""))]

    def alias_readers(self, alias: Alias) -> list[Reader]:
        return [reader for reader in self.all() if not self.is_locked(reader.name) and self.reads(reader, alias.expanded(""))]

    def refuse_plugin_alias_reader(self, reader: Reader) -> None:
        aliases = self.plugin_aliases_read(reader)
        if aliases:
            raise Rejection(f"the reader {reader.name} reads what journal {', journal '.join(alias.name for alias in aliases)} runs, which its plugin's own reader reads: a reader of the project never reads a plugin's alias")

    def reads_journal_output(self, reader: Reader) -> bool:
        aliases = self.aliases.index()
        return reader.name not in JOURNAL_COMMAND_READERS and any(name not in aliases for name in reader.commands.journal_commands())

    def default_names(self) -> set[str]:
        path = self.config.readers / DEFAULTS_FILE
        return set(path.read_text().split()) if path.is_file() else set()

    def default_choice(self, name: str) -> list[str]:
        reader = self.lookup(name)
        sharing_names = {candidate.name for candidate in self.all() if candidate.name != name and set(candidate.commands.programs) & set(reader.commands.programs)}
        default_names = (self.default_names() - sharing_names) | {name}
        (self.config.readers / DEFAULTS_FILE).write_text("\n".join(sorted(default_names)) + "\n")
        return sorted(sharing_names)

    def creation_seconds(self, reader: Reader) -> float:
        stats = [path.stat() for suffix in KINDS if (path := self.config.readers / f"{reader.name}{suffix}").is_file()]
        return min((getattr(stat, "st_birthtime", stat.st_mtime) for stat in stats), default=0.0)

    def stored_reader(self, name: str) -> Reader | None:
        rows = self.files(name)
        return Reader.loaded(rows[0]) if rows else None

    def add(self, reader: Reader) -> None:
        self.refuse_locked(reader.name, "replaced")
        self.stored_file(reader, ".pattern", reader.text())

    def add_script(self, reader: Reader, body: str) -> None:
        self.refuse_locked(reader.name, "replaced")
        self.stored_file(reader, ".sh", reader.script_text(body))

    # the journal's own write of a reader it ships
    def stock(self, reader: Reader) -> None:
        self.stored_file(reader, ".pattern", reader.text())

    # a reader written as one kind replaces one of the other kind by its name
    def stored_file(self, reader: Reader, suffix: str, text: str) -> None:
        if self.reads_journal_output(reader):
            raise Rejection(f"the reader {reader.name} would read a journal command's output, which the journal writes and shows whole itself: a reader reads a program's own output, such as pytest or go test, or an alias's run of one")
        name = reader.name
        self.config.readers.mkdir(parents=True, exist_ok=True)
        for kind in KINDS:
            (self.config.readers / f"{name}{kind}").unlink(missing_ok=True)
        (self.config.readers / f"{name}{suffix}").write_text(text)
