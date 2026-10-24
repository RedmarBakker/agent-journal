from datetime import datetime, timezone
from pathlib import Path
from journal.config import Config
from journal.repositories.aliases import Aliases
from journal.support.chain import Chain
from journal.features.shell.support.reader import Reader
from journal.features.shell.support.reader_commands import COMMANDS_PREFIX, ReaderCommands
from journal.features.shell.support.output_files import OutputFiles
from journal.models.command_output import CommandOutput
from journal.support.rejection import Rejection

JOURNAL = "journal"
# the readers chosen as their commands' defaults, one name a line, beside the readers
DEFAULTS_FILE = "defaults"

KINDS = (".pattern", ".sh")


class Readers:
    """The readers the project keeps in .journal/readers/, one file each, read by name; of several readers of one command the default reads it: the one the user chose, else the first made."""

    def __init__(self, config: Config, aliases: Aliases) -> None:
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

    def revisions(self) -> dict[str, datetime]:
        return {reader.name: datetime.fromtimestamp(self.file_stamp(reader.name), timezone.utc) for reader in self.all()}

    def file_stamp(self, name: str) -> float:
        return max((path.stat().st_mtime for path in self.files(name)), default=0.0)

    def reading_output(self, name: str, output: CommandOutput) -> Reader:
        reader = self.lookup(name)
        if reader.commands.programs and not any(reader.commands.is_read(line) for line in self.run_lines(output)):
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
        line_readers = next((found for part in Chain.choosing_parts(line) if (found := [reader for reader in readers if reader.commands.reads(part)])), [])
        default_names = self.default_names()
        return next((reader for reader in line_readers if reader.name in default_names), None) or min(line_readers, key=self.creation_seconds, default=None)

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

    def named(self, name: str) -> Reader | None:
        rows = self.files(name)
        return Reader.loaded(rows[0]) if rows else None

    def add(self, reader: Reader) -> None:
        self.written(reader.name, ".pattern", reader.text())

    def add_script(self, reader: Reader, body: str) -> None:
        self.written(reader.name, ".sh", reader.script_text(body))

    # a reader written as one kind replaces one of the other kind by its name
    def written(self, name: str, suffix: str, text: str) -> None:
        self.config.readers.mkdir(parents=True, exist_ok=True)
        for other in KINDS:
            (self.config.readers / f"{name}{other}").unlink(missing_ok=True)
        (self.config.readers / f"{name}{suffix}").write_text(text)
