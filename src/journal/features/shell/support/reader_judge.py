import re
from collections import Counter
from datetime import datetime, timedelta
from pathlib import Path

from journal.features.shell.support.card_line import CardLine
from journal.features.shell.support.output_files import OutputFiles
from journal.features.shell.support.progress_stalls import ProgressStalls
from journal.features.shell.support.reader import Reader
from journal.features.shell.support.readers import Readers
from journal.features.shell.support.streaming_form import StreamingForm
from journal.models.command_output import ACTIVE, FAILED, FINISHED, CommandOutput
from journal.repositories.command_outputs import CommandOutputs
from journal.models.reader_report import ReaderReport
from journal.support.command_shape import CommandShape
from journal.features.shell.shell_options import ShellOptions
from journal.repositories.reader_reports import ReaderReports
from journal.repositories.setting_rows import SettingRows

# a run at least this long needed its progress shown while it ran
PROGRESS_SECONDS = 30
# the longest a shown progress may stand still while its run goes on
STALL_SECONDS = 20
# the poor lines a report quotes
QUOTED_LINES = 3
# the newest runs looked through for a stored output of the command a new reader reads
NEWEST_RUNS = 200
COUNT_PATTERN = re.compile(r"\b(\d+)\s*/\s*(\d+)\b")
PERCENT_PATTERN = re.compile(r"\[\s*(\d+)%\]")
SUMMARY_PATTERN = re.compile(r"\b\d+\s+(?:passed|failed|skipped|errors?|tests?|warnings?|deselected)\b|\b(?:tests?|ran|finished|built|done)\b.*\b(?:in|took)\s+[\d.]+\s*m?s\b", re.IGNORECASE)
PROGRESS_MISSING = "its card showed no progress"
PROGRESS_STALLED = "its progress stood still for"
SUMMARY_MISSING = "the card ended with no line of its own"
POOR_LINES = "the card showed lines too long"
SINGLE_WORD = "the card showed a line of one word"
FINDING_KINDS = (POOR_LINES, SINGLE_WORD, PROGRESS_MISSING, PROGRESS_STALLED, SUMMARY_MISSING)


class ReaderJudge:
    """Judges what a reader showed of a run once it ended: lines short and readable, its progress shown while a long run went, and a summary at the end; whatever falls short becomes a report with its evidence and the fix for that tool."""

    def __init__(self, readers: Readers, outputs: CommandOutputs, stalls: ProgressStalls, reports: ReaderReports, settings: SettingRows) -> None:
        self.readers, self.outputs, self.stalls, self.reports, self.settings = readers, outputs, stalls, reports, settings

    def latest_stored_run(self, reader: Reader) -> CommandOutput | None:
        runs = self.outputs.latest(NEWEST_RUNS)
        return next((run for run in runs if reader.commands.is_shown_run(run.command) and OutputFiles(Path(run.folder)).is_stored()), None)

    def report(self, output: CommandOutput, ended_at: datetime) -> ReaderReport | None:
        reader = self.readers.found(output.watch_reader)
        files = OutputFiles(Path(output.folder))
        if reader is None or reader.script or not files.is_stored() or reader.commands.programs and not reader.commands.is_shown_run(output.command):
            return None
        lines = files.lines()
        candidates = [*self.poor_lines(reader, output, lines), *self.single_word_lines(reader, output, lines), *self.missing_progress(reader, output, lines, ended_at), *self.stalled_progress(output), *self.missing_summary(reader, output, lines)]
        kinds = self.dismissal_kinds(output.command, ended_at)
        shortfalls = [shortfall for shortfall in candidates if not any(kind in shortfall[0] for kind in kinds)]
        if not shortfalls:
            return None
        return ReaderReport(environment_id=output.environment_id, reader=reader.name, output=output.id, command=output.command, session=output.session, findings=tuple(shortfall[0] for shortfall in shortfalls), fixes=tuple(shortfall[1] for shortfall in shortfalls))

    def dismissal_kinds(self, command: str, time: datetime) -> set[str]:
        limit = self.settings.integer(ShellOptions.DISMISSAL_LIMIT)
        if not limit:
            return set()
        name = CommandShape.command_name(command)
        reports = self.reports.dismissed_reports(time - timedelta(hours=self.settings.integer(ShellOptions.PAUSE_HOURS)))
        counts = Counter(kind for report in reports if CommandShape.command_name(report.command) == name for kind in FINDING_KINDS if any(kind in finding for finding in report.findings))
        return {kind for kind, count in counts.items() if count >= limit}

    def poor_lines(self, reader: Reader, output: CommandOutput, lines: list[str]) -> list[tuple[str, str]]:
        poor = [line for line in reader.variant(output.stage()).card_lines(lines) if CardLine.is_poor(CardLine.plain(line))][:QUOTED_LINES]
        if not poor:
            return []
        quoted = "; ".join(f'"{line[:120]}"' for line in poor)
        return [(f"{POOR_LINES} or too much like code to read at a glance: {quoted}", "narrow the pattern to the short lines a person reads, such as the failures' names and the summary")]

    def single_word_lines(self, reader: Reader, output: CommandOutput, lines: list[str]) -> list[tuple[str, str]]:
        single = [line for line in reader.variant(output.stage()).card_lines(lines) if len(CardLine.plain(line).split()) == 1][:QUOTED_LINES]
        if not single:
            return []
        return [(f"{SINGLE_WORD}, which says nothing of the run: {self.quoted(single)}", "give the reader a pattern that picks a line saying what the run is doing, in several words")]

    def missing_progress(self, reader: Reader, output: CommandOutput, lines: list[str], ended_at: datetime) -> list[tuple[str, str]]:
        seconds = (ended_at - output.creation_time).total_seconds()
        if seconds < PROGRESS_SECONDS or reader.progress(lines).is_known() or not self.has_progress(lines):
            return []
        return [(f"the run took {seconds:.0f} seconds and {PROGRESS_MISSING}", self.progress_fix(output.command, lines))]

    def stalled_progress(self, output: CommandOutput) -> list[tuple[str, str]]:
        seconds = self.stalls.longest_seconds(output.row_id)
        if seconds <= STALL_SECONDS:
            return []
        return [(f"{PROGRESS_STALLED} {seconds:.0f} seconds while the run went on", "make the run print its progress as it goes, not only when a part of it ends, or give the reader a --progress pattern that picks a figure printed more often")]

    @staticmethod
    def has_progress(lines: list[str]) -> bool:
        return any(PERCENT_PATTERN.search(line) or COUNT_PATTERN.search(line) for line in lines)

    def missing_summary(self, reader: Reader, output: CommandOutput, lines: list[str]) -> list[tuple[str, str]]:
        if reader.variant(output.stage()).card_lines(lines) or not lines:
            return []
        return [(f"{SUMMARY_MISSING}; the run's last line was \"{lines[-1][:120]}\"", "give the reader a --finished and a --failed pattern for the summary line, or make the run print one")]

    def misses(self, reader: Reader, lines: list[str]) -> list[str]:
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
        stored = self.outputs.matching(id=report.output)
        reader = self.readers.stored_reader(report.reader)
        if not stored or reader is None or not OutputFiles(Path(stored[0].folder)).is_stored():
            return []
        output = stored[0]
        files = OutputFiles(Path(output.folder))
        lines = files.lines()
        fixes = []
        progress_unshown = any(PROGRESS_MISSING in finding for finding in report.findings) and not reader.progress(lines).is_known() and self.has_progress(lines)
        if progress_unshown:
            fixes.append(self.progress_fix(output.command, lines))
        if any(PROGRESS_STALLED in finding for finding in report.findings) and self.stalls.longest_seconds(output.row_id) > STALL_SECONDS:
            fixes.append(f"{PROGRESS_STALLED} {self.stalls.longest_seconds(output.row_id):.0f} seconds while the run went on: make it print its progress as it goes")
        summary = next((line for line in lines if SUMMARY_PATTERN.search(line)), "")
        summary_unpicked = any(SUMMARY_MISSING in finding for finding in report.findings) and bool(summary) and not reader.variant(output.stage()).card_lines(lines)
        if summary_unpicked:
            fixes.append(f"the run printed a summary, \"{summary[:120]}\": give the reader a --finished pattern that picks it, such as '{re.escape(summary.split()[0]) if summary.split() else summary}'")
        return fixes

    @staticmethod
    def progress_fix(command: str, lines: list[str]) -> str:
        if any(PERCENT_PATTERN.search(line) for line in lines):
            return "the run prints a percentage: give the reader --progress '\\[\\s*(\\d+)%\\]'"
        if any(COUNT_PATTERN.search(line) for line in lines):
            return "the run prints a count of a total: give the reader --progress '(\\d+)/(\\d+)'"
        return StreamingForm.advice(CommandShape.command_name(command))
