from datetime import datetime, timedelta
from pathlib import Path

from journal.features.shell.support.count_forms import CountForms
from journal.features.shell.support.output_files import OutputFiles
from journal.features.shell.support.reader import Reader
from journal.features.shell.support.reader_judge import PROGRESS_MISSING, STOPPED_PICKING, UNFILTERED, ReaderJudge
from journal.features.shell.support.readers import SHIPPED_READERS, Readers
from journal.features.shell.shell_options import ShellOptions
from journal.models.command_output import CommandOutput
from journal.models.reader_report import ReaderReport
from journal.repositories.reader_reports import ReaderReports
from journal.repositories.setting_rows import SettingRows
from journal.support.actor import Actor
from journal.support.command_shape import CommandShape

# the newest lines of a running output its reader is judged on
NEWEST_LINES = 40
# the share of the newest lines a reader may pick before its card is the raw output
UNFILTERED_SHARE = 0.9
WATCHED_RUN_FINDINGS = (UNFILTERED, STOPPED_PICKING, PROGRESS_MISSING)


class WatchedRunJudge:
    """Judges a watched run's reader against what the run prints while it goes on, not only when the reader was added: a card that shows nearly every line, a reader that fitted the start of the run and picks nothing of what it prints now, and a run that prints a count of a total its reader does not show each raise a report at once; and a dismissed report of the same finding for the same command is opened again, since the run shows the dismissal was wrong."""

    def __init__(self, readers: Readers, reports: ReaderReports, judge: ReaderJudge, settings: SettingRows) -> None:
        self.readers, self.reports, self.judge, self.settings = readers, reports, judge, settings

    def judged(self, output: CommandOutput, time: datetime) -> None:
        reader = self.readers.found(output.watch_reader)
        files = OutputFiles(Path(output.folder))
        if reader is None or reader.script or reader.name in SHIPPED_READERS or not files.is_stored():
            return
        shortfalls = [shortfall for shortfall in self.findings(reader, ReaderJudge.read_lines(reader, files)) if not self.reports.open_with_output_finding(output.row_id, shortfall[0])]
        if not shortfalls:
            return
        self.reports.save(ReaderReport(environment_id=output.environment_id, reader=reader.name, output=output.row_id, command=output.command, session=output.session, findings=tuple(finding for finding, _ in shortfalls), fixes=tuple(fix for _, fix in shortfalls)), Actor.system())
        self.contradicted(output.command, {finding for finding, _ in shortfalls}, time)

    def findings(self, reader: Reader, lines: list[str]) -> list[tuple[str, str]]:
        return [*self.unfiltered(reader, lines), *self.stopped_picking(reader, lines), *self.unshown_progress(reader, lines)]

    @staticmethod
    def unfiltered(reader: Reader, lines: list[str]) -> list[tuple[str, str]]:
        newest = [line for line in lines[-NEWEST_LINES:] if line.strip()]
        if len(newest) < NEWEST_LINES // 2 or len(reader.card_lines(newest)) < UNFILTERED_SHARE * len(newest):
            return []
        return [(f"{UNFILTERED}: it picked {len(reader.card_lines(newest))} of the {len(newest)} newest lines", "narrow the pattern to the few lines a person reads: the failures, the progress and the summary")]

    @staticmethod
    def stopped_picking(reader: Reader, lines: list[str]) -> list[tuple[str, str]]:
        start, newest = lines[:-NEWEST_LINES], lines[-NEWEST_LINES:]
        if len(newest) < NEWEST_LINES or not reader.card_lines(start) or reader.card_lines(newest) or any(reader.is_progress_line(line) for line in newest):
            return []
        return [(f"{STOPPED_PICKING}, such as {ReaderJudge.quoted(newest[-3:])}", "write the reader for the lines the run prints while it does its work, not for the lines of its start such as an image build")]

    @staticmethod
    def unshown_progress(reader: Reader, lines: list[str]) -> list[tuple[str, str]]:
        if not CountForms.has_total(lines) or reader.progress(lines).is_known():
            return []
        return [(f"while the run went on {PROGRESS_MISSING}, though it printed {ReaderJudge.quoted(CountForms.progress_lines(lines)[-3:])}", ReaderJudge.progress_fix("", lines))]

    def contradicted(self, command: str, findings: set[str], time: datetime) -> None:
        name = CommandShape.command_name(command)
        for report in self.reports.dismissed_reports(time - timedelta(hours=self.settings.integer(ShellOptions.PAUSE_HOURS))):
            kinds = {kind for kind in WATCHED_RUN_FINDINGS if any(kind in finding for finding in report.findings)}
            if CommandShape.command_name(report.command) == name and any(kind in finding for kind in kinds for finding in findings):
                self.reports.save(report.contradicted(f"a later run of {name} showed the same while it ran, so the dismissal \"{report.dismissal}\" was wrong", time), Actor.system())
