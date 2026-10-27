from pathlib import Path

from journal.features.shell.support.output_files import OutputFiles
from journal.features.shell.support.reader import Reader
from journal.features.shell.support.reader_commands import ReaderCommands
from journal.features.shell.support.reader_judge import ReaderJudge
from journal.features.shell.support.reader_probes import ReaderProbes
from journal.features.shell.support.readers import Readers
from journal.features.shell.support.starting_readers import StartingReaders
from journal.models.command_output import CommandOutput
from journal.support.command_classifier import CommandClassifier
from journal.support.command_shape import CommandShape


class ReaderGuess:
    """The reader a command moved to the background gets when no reader reads it: a reader the project has for the same kind of run that reads this run well, the command added to its commands so readers never multiply, else the starting reader of the run's kind filled from its own output; tried on the output, and refused when it picks no line or every line, before it is saved."""

    def __init__(self, readers: Readers, judge: ReaderJudge, shapes: CommandShape, classifier: CommandClassifier, starting: StartingReaders) -> None:
        self.readers, self.judge, self.shapes, self.classifier, self.starting = readers, judge, shapes, classifier, starting

    def guessed(self, output: CommandOutput, part: str) -> Reader | None:
        files = OutputFiles(Path(output.folder))
        lines = files.lines() if files.is_stored() else []
        name = self.shapes.command_name(part)
        if not lines or not name:
            return None
        shared = self.shared(part, name, lines)
        if shared is not None:
            return shared
        reader = self.starting.filled(self.classifier.classify(part), name, lines)
        if reader is None or not self.reads_well(reader, lines):
            return None
        if self.readers.stored_reader(reader.name) is None:
            self.readers.add(reader)
        return self.readers.stored_reader(reader.name)

    def shared(self, part: str, name: str, lines: list[str]) -> Reader | None:
        kind = self.classifier.classify(part).kind
        reader = next((reader for reader in self.readers.all() if not self.readers.is_locked(reader.name) and not reader.script and self.is_kind(reader, kind) and self.reads_well(reader, lines)), None)
        if reader is None:
            return None
        if not self.readers.reads(reader, part):
            self.readers.add(reader.revised(commands=ReaderCommands((*reader.commands.programs, name))))
        return self.readers.stored_reader(reader.name)

    def is_kind(self, reader: Reader, kind: str) -> bool:
        return any(self.classifier.classify(program).kind == kind for program in reader.commands.programs)

    def reads_well(self, reader: Reader, lines: list[str]) -> bool:
        return not self.judge.misses(reader, lines) and not ReaderProbes.unfiltered_patterns(reader)
