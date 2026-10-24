import re
from datetime import datetime
from pathlib import Path

from journal.features.shell.support.card_line import CardLine
from journal.features.shell.support.output_files import OutputFiles
from journal.features.shell.support.reader import Reader
from journal.features.shell.support.readers import Readers
from journal.features.shell.support.streaming_form import StreamingForm
from journal.models.command_output import ACTIVE, FAILED, FINISHED, CommandOutput
from journal.repositories.command_outputs import CommandOutputs
from journal.models.reader_report import ReaderReport
from journal.support.command_shape import CommandShape

# a run at least this long needed its progress shown while it ran
PROGRESS_SECONDS = 30
# the poor lines a report quotes
QUOTED_LINES = 3
COUNT_PATTERN = re.compile(r"\b(\d+)\s*/\s*(\d+)\b")
PERCENT_PATTERN = re.compile(r"\[\s*(\d+)%\]|\b(\d+)%")
SUMMARY_PATTERN = re.compile(r"\b\d+\s+(?:passed|failed|skipped|errors?|tests?|warnings?|deselected)\b|\b(?:tests?|ran|finished|built|done)\b.*\b(?:in|took)\s+[\d.]+\s*m?s\b", re.IGNORECASE)
PROGRESS_MISSING = "its card showed no progress"
SUMMARY_MISSING = "the card ended with no line of its own"


class ReaderJudge:
    """Judges what a reader showed of a run once it ended: lines short and readable, its progress shown while a long run went, and a summary at the end; whatever falls short becomes a report with its evidence and the fix for that tool."""

    def __init__(self, readers: Readers, outputs: CommandOutputs) -> None:
        self.readers, self.outputs = readers, outputs

    def report(self, output: CommandOutput, ended_at: datetime) -> ReaderReport | None:
        reader = self.readers.lookup(output.watch_reader)
        files = OutputFiles(Path(output.folder))
        if reader.script or not files.is_stored() or reader.commands.programs and not reader.commands.is_shown_run(output.command):
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
        return [(f"the run took {seconds:.0f} seconds and {PROGRESS_MISSING}", self.progress_fix(output.command, lines))]

    def missing_summary(self, reader: Reader, output: CommandOutput, lines: list[str]) -> list[tuple[str, str]]:
        if reader.variant(output.stage()).card_lines(lines) or not lines:
            return []
        return [(f"{SUMMARY_MISSING}; the run's last line was \"{lines[-1][:120]}\"", "give the reader a --finished and a --failed pattern for the summary line, or make the run print one")]

    def tried(self, reader: Reader, lines: list[str]) -> list[str]:
        """What a reader misses of a run's lines: it picks none, it shows no progress the run printed, or it does not end on the summary the run printed; each with the lines it should have matched."""
        misses = []
        if lines and not any(reader.variant(stage).card_lines(lines) for stage in (ACTIVE, FINISHED, FAILED)):
            misses.append(f"it picks no line of the run, whose last lines were {self.quoted(lines[-QUOTED_LINES:])}")
        progress_lines = [line for line in lines if PERCENT_PATTERN.search(line) or COUNT_PATTERN.search(line)]
        if progress_lines and not reader.progress(lines).is_known():
            misses.append(f"it shows no progress, though the run printed {self.quoted(progress_lines[-QUOTED_LINES:])}: {self.progress_fix('', lines)}")
        summary = next((line for line in reversed(lines) if SUMMARY_PATTERN.search(line)), "")
        if summary and summary not in reader.variant(FINISHED).card_lines(lines):
            misses.append(f"it does not end on a line of its own, though the run printed the summary {self.quoted([summary])}: give it a --finished pattern that picks it")
        return misses

    @staticmethod
    def quoted(lines: list[str]) -> str:
        return "; ".join(f'"{line[:120]}"' for line in lines)

    def run_findings(self, report: ReaderReport) -> list[str]:
        """What the report's findings say the card missed that the run's own output printed, each with the fix, while the reader still misses it."""
        stored = self.outputs.matching(id=report.output)
        reader = self.readers.named(report.reader)
        if not stored or reader is None or not OutputFiles(Path(stored[0].folder)).is_stored():
            return []
        output = stored[0]
        files = OutputFiles(Path(output.folder))
        lines = files.lines()
        fixes = []
        if any(PROGRESS_MISSING in finding for finding in report.findings) and not reader.progress(lines).is_known() and any(PERCENT_PATTERN.search(line) or COUNT_PATTERN.search(line) for line in lines):
            fixes.append(self.progress_fix(output.command, lines))
        summary = next((line for line in lines if SUMMARY_PATTERN.search(line)), "")
        if any(SUMMARY_MISSING in finding for finding in report.findings) and summary and not reader.variant(output.stage()).card_lines(lines):
            fixes.append(f"the run printed a summary, \"{summary[:120]}\": give the reader a --finished pattern that picks it, such as '{re.escape(summary.split()[0]) if summary.split() else summary}'")
        return fixes

    @staticmethod
    def progress_fix(command: str, lines: list[str]) -> str:
        if any(PERCENT_PATTERN.search(line) for line in lines):
            return "the run prints a percentage: give the reader --progress '\\[\\s*(\\d+)%\\]'"
        if any(COUNT_PATTERN.search(line) for line in lines):
            return "the run prints a count of a total: give the reader --progress '(\\d+)/(\\d+)'"
        return StreamingForm.advice(CommandShape.command_name(command))
