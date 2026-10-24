import re
from datetime import datetime
from pathlib import Path

from journal.features.shell.support.card_line import CardLine
from journal.features.shell.support.output_files import OutputFiles
from journal.features.shell.support.reader import Reader
from journal.features.shell.support.readers import Readers
from journal.features.shell.support.streaming_form import StreamingForm
from journal.models.command_output import CommandOutput
from journal.models.reader_report import ReaderReport
from journal.support.command_shape import CommandShape

# a run at least this long needed its progress shown while it ran
PROGRESS_SECONDS = 30
# the poor lines a report quotes
QUOTED_LINES = 3
COUNT_PATTERN = re.compile(r"\b(\d+)\s*/\s*(\d+)\b")
PERCENT_PATTERN = re.compile(r"\[\s*(\d+)%\]|\b(\d+)%")


class ReaderJudge:
    """Judges what a reader showed of a run once it ended: lines short and readable, its progress shown while a long run went, and a summary at the end; whatever falls short becomes a report with its evidence and the fix for that tool."""

    def __init__(self, readers: Readers) -> None:
        self.readers = readers

    def report(self, output: CommandOutput, ended_at: datetime) -> ReaderReport | None:
        reader = self.readers.lookup(output.watch_reader)
        files = OutputFiles(Path(output.folder))
        if not isinstance(reader, Reader) or not files.is_stored() or reader.commands.programs and not reader.commands.is_shown_run(output.command):
            return None
        lines = files.lines()
        shortfalls = [*self.poor_lines(reader, output, lines), *self.missing_progress(reader, output, lines, ended_at), *self.missing_summary(reader, output, lines)]
        if not shortfalls:
            return None
        return ReaderReport(environment_id=output.environment_id, reader=reader.name, output=output.id, command=output.command, session=output.session, findings=tuple(shortfall[0] for shortfall in shortfalls), fixes=tuple(shortfall[1] for shortfall in shortfalls))

    def poor_lines(self, reader: Reader, output: CommandOutput, lines: list[str]) -> list[tuple[str, str]]:
        poor = [line for line in reader.variant(output.stage()).card_lines(lines) if CardLine.is_poor(CardLine.plain(line))][:QUOTED_LINES]
        if not poor:
            return []
        quoted = "; ".join(f'"{line[:120]}"' for line in poor)
        return [(f"the card showed lines too long or too much like code to read at a glance: {quoted}", "narrow the pattern to the short lines a person reads, such as the failures' names and the summary")]

    def missing_progress(self, reader: Reader, output: CommandOutput, lines: list[str], ended_at: datetime) -> list[tuple[str, str]]:
        seconds = (ended_at - output.creation_time).total_seconds()
        if seconds < PROGRESS_SECONDS or reader.progress(lines).is_known():
            return []
        return [(f"the run took {seconds:.0f} seconds and its card showed no progress", self.progress_fix(output, lines))]

    def missing_summary(self, reader: Reader, output: CommandOutput, lines: list[str]) -> list[tuple[str, str]]:
        if reader.variant(output.stage()).card_lines(lines) or not lines:
            return []
        return [(f"the card ended with no line of its own; the run's last line was \"{lines[-1][:120]}\"", "give the reader a --finished and a --failed pattern for the summary line, or make the run print one")]

    @staticmethod
    def progress_fix(output: CommandOutput, lines: list[str]) -> str:
        if any(PERCENT_PATTERN.search(line) for line in lines):
            return "the run prints a percentage: give the reader --progress '\\[\\s*(\\d+)%\\]'"
        if any(COUNT_PATTERN.search(line) for line in lines):
            return "the run prints a count of a total: give the reader --progress '(\\d+)/(\\d+)'"
        return StreamingForm.advice(CommandShape.command_name(output.command))
