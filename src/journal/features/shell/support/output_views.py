import time
from dataclasses import replace
from pathlib import Path

from journal.features.shell.support.card_line import CardLine
from journal.features.shell.support.output_files import OutputFiles
from journal.features.shell.support.output_view import OutputView
from journal.features.shell.support.progress import Progress
from journal.features.shell.support.reader import Reader
from journal.features.shell.support.readers import Readers
from journal.features.shell.support.step_tally import StepTally
from journal.models.command_output import CommandOutput
from journal.repositories.command_outputs import CommandOutputs
from journal.support.time_source import TimeSource

TAIL_LINES = 10
# the lines of how a run ended that the agent is told, its progress lines left on the card
SUMMARY_LINES = 3
VIEW_LINES = 20
SILENT_SECONDS = 30
# the card of a run that has printed nothing for SILENT_SECONDS says why, since no reader can show what was never printed
SILENT_CARD_LINE = "nothing printed yet: the command buffers its output"
# the card of a run whose progress is complete while its command goes on says what that means
COMPLETE_UNENDED_LINE = "at 100% but still running: it waits on something its reader does not read"


class OutputViews:
    """The view of a watched output, read from its files through its reader, and the lines, progress and silence its process card shows. The progress is the run's as it prints it, or, running and before it prints a count, its steps so far against the steps the same command line's last run took."""

    def __init__(self, readers: Readers, outputs: CommandOutputs, time_source: TimeSource) -> None:
        self.time_source = time_source
        self.readers, self.outputs = readers, outputs

    def view(self, output: CommandOutput) -> OutputView:
        measured = self.measured(output)
        return replace(measured, silent=self.is_silent(output, measured), complete_unended=output.is_complete_reported and not output.ended)

    def reader(self, output: CommandOutput) -> Reader | None:
        return self.readers.found(output.watch_reader)

    def is_silent(self, output: CommandOutput, view: OutputView) -> bool:
        return not output.ended and self.time_source.seconds() - output.creation_time.timestamp() >= SILENT_SECONDS and not view.figure and not self.card_lines(output, view)

    def measured(self, output: CommandOutput) -> OutputView:
        files = OutputFiles(Path(output.folder))
        ending = output.ending() if output.ended else ""
        if not files.is_stored():
            return OutputView.unmeasured(output.row_id, (), ending)
        watching = self.reader(output)
        if watching is None:
            return OutputView.unmeasured(output.row_id, tuple(files.last(TAIL_LINES)), ending)
        reader, lines = watching.variant(output.stage()), files.lines()
        progress = self.progress(output, reader, lines)
        tally = reader.tally(lines) if not output.ended else StepTally(0, 0)
        figure = " · ".join(part for part in (progress.text() if progress.is_known() else "", tally.text() if tally.is_known() else "") if part)
        return OutputView(output.row_id, tuple(reader.read(lines)[-VIEW_LINES:]), figure, progress.fraction(), ending, is_counting=reader.is_counting())

    def progress(self, output: CommandOutput, reader: Reader, lines: list[str]) -> Progress:
        count_progress = reader.progress(lines)
        if count_progress.is_known() or output.ended or not reader.is_counting():
            return count_progress
        last_run = self.outputs.previous_run(output)
        return Progress.estimated(self.steps(reader.tally(lines)), self.run_steps(last_run, reader), reader.label) if last_run else count_progress

    def run_steps(self, output: CommandOutput, reader: Reader) -> int:
        files = OutputFiles(Path(output.folder))
        return self.steps(reader.tally(files.lines())) if files.is_stored() else 0

    @staticmethod
    def steps(tally: StepTally) -> int:
        return tally.passed + tally.failed

    def card_lines(self, output: CommandOutput, view: OutputView) -> tuple[str, ...]:
        files = OutputFiles(Path(output.folder))
        watching = self.reader(output)
        if watching is None or not files.is_stored():
            return view.lines
        reader, lines = watching.variant(output.stage()), files.lines()
        summary_lines = tuple(CardLine.plain(line) for line in reader.card_lines(lines)[-VIEW_LINES:])
        return summary_lines or self.tally_lines(output, reader.tally(lines))

    @staticmethod
    def tally_lines(output: CommandOutput, tally: StepTally) -> tuple[str, ...]:
        return (tally.text(),) if output.ended and tally.is_known() else ()

    def summary(self, output: CommandOutput) -> str:
        files = OutputFiles(Path(output.folder))
        watching = self.reader(output)
        if not output.ended or watching is None or not files.is_stored():
            return ""
        return watching.summary(files.lines())

    def is_summary_missing(self, output: CommandOutput) -> bool:
        files = OutputFiles(Path(output.folder))
        watching = self.reader(output)
        if not output.ended or watching is None or not files.is_stored():
            return False
        reader, lines = watching.variant(output.stage()), files.lines()
        return not reader.card_lines(lines) and reader.tally(lines).is_known()

    @staticmethod
    def ending_lines(output: CommandOutput) -> tuple[str, ...]:
        return (output.ending(),) if output.ended else ()

    def is_empty_card(self, output: CommandOutput, view: OutputView) -> bool:
        return self.reader(output) is not None and output.ended and not self.card_lines(output, view) and not view.figure

    def poor_line(self, output: CommandOutput, view: OutputView) -> str:
        return next((line for line in self.card_lines(output, view) if self.reader(output) is not None and CardLine.is_poor(line)), "")

    def count(self, output: CommandOutput) -> str:
        files = OutputFiles(Path(output.folder))
        reader = self.reader(output)
        if reader is None or not files.is_stored():
            return ""
        lines = files.lines()
        progress, tally = self.progress(output, reader, lines), reader.tally(lines)
        steps = progress.count_text() if progress.is_known() and not output.ended else ""
        counted = " · ".join(part for part in (steps, tally.text() if tally.is_known() else "") if part)
        return counted or (self.zero_count(reader) if not output.ended else "")

    @staticmethod
    def zero_count(reader: Reader) -> str:
        if reader.step_pattern:
            return "0 passed"
        return "0%" if reader.progress_pattern else ""

    def ended_summary(self, output: CommandOutput) -> str | None:
        reader = self.reader(output)
        if reader is None:
            return None
        lines = self.card_lines(output, self.view(output))
        ending = [line for line in lines if not reader.is_progress_line(line)] or list(lines[-1:])
        return " / ".join(ending[-SUMMARY_LINES:]) or None

    def card_text(self, output: CommandOutput, view: OutputView) -> str:
        return "\n".join([*(self.card_lines(output, view) or self.ending_lines(output) or self.silent_lines(view)), *self.complete_unended_lines(view)])

    @staticmethod
    def complete_unended_lines(view: OutputView) -> tuple[str, ...]:
        return (COMPLETE_UNENDED_LINE,) if view.complete_unended else ()

    @staticmethod
    def silent_lines(view: OutputView) -> tuple[str, ...]:
        return (SILENT_CARD_LINE,) if view.silent else ()
