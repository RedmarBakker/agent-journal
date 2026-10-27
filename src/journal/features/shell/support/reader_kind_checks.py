from pathlib import Path

from journal.features.shell.support.output_files import OutputFiles
from journal.features.shell.support.reader import Reader
from journal.features.shell.support.reader_judge import QUOTED_LINES, TEST_TOTALS, ReaderJudge
from journal.features.shell.support.readers import Readers
from journal.models.command_output import FAILED, FINISHED, CommandOutput
from journal.repositories.aliases import Aliases
from journal.support.command_classifier import CommandClassifier


class ReaderKindChecks:
    """What a reader being added misses of the stored runs by the kind of run it reads: its progress pattern matching no line of the run it was written from, and a test run's reader showing no counts on a passing or a failing run when both are stored; a script and a reader an alias names are left to the reader judge."""

    def __init__(self, judge: ReaderJudge, readers: Readers, aliases: Aliases, classifier: CommandClassifier) -> None:
        self.judge, self.readers, self.aliases, self.classifier = judge, readers, aliases, classifier

    def misses(self, reader: Reader, runs: list[CommandOutput]) -> list[str]:
        if reader.script or not runs or self.aliases.reader_rows(reader.name):
            return []
        return [*self.unmatched_progress(reader, runs[0]), *self.uncounted_test_runs(reader, runs)]

    def unmatched_progress(self, reader: Reader, run: CommandOutput) -> list[str]:
        lines = self.judge.read_lines(reader, OutputFiles(Path(run.folder)))
        if not reader.is_counting() or not lines or any(reader.is_progress_line(line) for line in lines):
            return []
        return [f"its --progress matches no line of output {run.id}, the run it was written from, whose last lines were {self.judge.quoted(lines[-QUOTED_LINES:])}: {self.judge.progress_fix('', lines)}"]

    def uncounted_test_runs(self, reader: Reader, runs: list[CommandOutput]) -> list[str]:
        passing = next((run for run in runs if run.status == 0), None)
        failing = next((run for run in runs if run.status != 0), None)
        if passing is None or failing is None or not self.classifier.classify(self.readers.read_part(reader, runs[0].command)).is_test_run:
            return []
        return [*self.uncounted(reader, passing, FINISHED, "passing"), *self.uncounted(reader, failing, FAILED, "failing")]

    def uncounted(self, reader: Reader, run: CommandOutput, stage: str, outcome: str) -> list[str]:
        lines = self.judge.read_lines(reader, OutputFiles(Path(run.folder)))
        counts = next((line for line in reversed(lines) if TEST_TOTALS.search(line)), "")
        if not counts or any(TEST_TOTALS.search(line) for line in reader.variant(stage).card_lines(lines)):
            return []
        return [f"it shows no counts of the {outcome} run, output {run.id}, though the run printed {self.judge.quoted([counts])}: give it a --{stage} pattern that picks that line"]
