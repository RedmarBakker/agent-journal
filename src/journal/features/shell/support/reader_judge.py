import re
from collections import Counter
from datetime import datetime, timedelta
from pathlib import Path

from journal.features.shell.support.activity_label import ActivityLabel
from journal.features.shell.support.git_commands import GitCommands
from journal.features.shell.support.card_line import CardLine
from journal.features.shell.support.count_forms import PERCENT_PATTERN, CountForms
from journal.features.shell.support.output_files import STYLE_CODES, OutputFiles
from journal.features.shell.support.output_silences import OutputSilences
from journal.features.shell.support.progress_stalls import ProgressStalls
from journal.features.shell.support.reader import Reader
from journal.features.shell.support.run_processes import RunProcesses
from journal.features.shell.support.readers import Readers
from journal.features.shell.support.streaming_form import StreamingForm
from journal.models.command_output import ACTIVE, FAILED, FINISHED, CommandOutput
from journal.repositories.command_outputs import CommandOutputs
from journal.repositories.run_history import RunHistory
from journal.models.alias import Alias
from journal.repositories.aliases import Aliases
from journal.models.reader_report import ReaderReport
from journal.support.command_classifier import CommandClassifier
from journal.support.command_shape import CommandShape
from journal.features.shell.shell_options import ShellOptions
from journal.repositories.reader_reports import ReaderReports
from journal.repositories.setting_rows import SettingRows

# a run at least this long needed its progress shown while it ran
PROGRESS_SECONDS = 30
# the longest a shown progress may stand still while its run goes on
STALL_SECONDS = 20
# the times a card's progress must have moved for the run to count as printing its count regularly, so one slow stretch in it is no finding
REGULAR_PROGRESS_CHANGES = 5
# the poor lines a report quotes
QUOTED_LINES = 3
# the newest runs looked through for a stored output of the command a new reader reads
NEWEST_RUNS = 200
SUMMARY_PATTERN = re.compile(r"\b\d+\s+(?:passed|failed|skipped|errors?|tests?|warnings?|deselected)\b|\b(?:tests?|ran|finished|built|done)\b.*\b(?:in|took)\s+[\d.]+\s*m?s\b", re.IGNORECASE)
PROGRESS_MISSING = "its card showed no progress"
PROGRESS_STALLED = "its progress stood still for"
BUILD_UNSHOWN = "the build's card showed nothing moving"
PROGRESS_LATE = "its progress showed only in the last lines"
SUMMARY_MISSING = "the card ended with no line of its own"
POOR_LINES = "the card showed lines too long"
SINGLE_WORD = "the card showed a line of one word"
SUMMARY_READER_MISSING = "its card had no summary reader"
MIXED_TITLE = "its title was given to runs that do different things"
SINGLE_WORD_TITLE = "its card is titled by a bare word"
TOTAL_MISSING = "the run prints a counter and no total"
SUITES_COUNTED = "its progress counts suites, not tests"
SILENT_RUN = "the run printed nothing for"
UNFILTERED = "its card showed nearly every line of the run, so it filtered nothing"
STOPPED_PICKING = "it picked lines at the start of the run and none of its newest"
FINDING_KINDS = (UNFILTERED, STOPPED_PICKING, POOR_LINES, SINGLE_WORD, PROGRESS_MISSING, PROGRESS_STALLED, PROGRESS_LATE, BUILD_UNSHOWN, SUMMARY_MISSING, SUMMARY_READER_MISSING, MIXED_TITLE, SINGLE_WORD_TITLE, TOTAL_MISSING, SUITES_COUNTED, SILENT_RUN)
# the newest runs of a reader looked through for one title given to different work
MIXED_RUNS = 6
# a total past this is no count of a run's work but a number such as a job's id
LARGEST_TOTAL = 1_000_000
TEST_TOTALS = re.compile(r"\b\d+\s+(?:passed|failed|tests?)\b|^\s*Tests?\s+\d+|^\s*Test Files\b", re.IGNORECASE)
BUILD_LINE = re.compile(r"\bbuilt in\b|\bbuild (?:succeeded|complete|finished)\b", re.IGNORECASE)
# the flags that only ask a program its version or its help, so a part that carries one, or whose standard output goes to a file, shows no run of it on a card
HELP_FLAGS = ("--version", "--help", "-h", "-V")


class ReaderJudge:
    """Judges what a reader showed of a run once it ended: lines short and readable, its progress shown while a long run went, and a summary at the end; a run that printed nothing for a long stretch is the command's fault, buffering, and is said so in place of the reader's progress findings; whatever falls short becomes a report with its evidence and the fix for that tool."""

    def __init__(self, readers: Readers, outputs: CommandOutputs, stalls: ProgressStalls, reports: ReaderReports, settings: SettingRows, history: RunHistory, processes: RunProcesses, silences: OutputSilences, aliases: Aliases, labels: ActivityLabel, classifier: CommandClassifier) -> None:
        self.labels, self.classifier = labels, classifier
        self.readers, self.outputs, self.stalls, self.reports, self.settings = readers, outputs, stalls, reports, settings
        self.history, self.processes, self.silences, self.aliases = history, processes, silences, aliases

    def stored_runs(self, reader: Reader) -> list[CommandOutput]:
        return self.history.latest_accepted(NEWEST_RUNS, lambda run: self.is_shown_run(reader.commands.read_part(run.command)) and OutputFiles(Path(run.folder)).is_stored())

    def is_shown_run(self, part: str) -> bool:
        return bool(part) and not self.classifier.redirects_output(part) and not any(flag in part.split() for flag in HELP_FLAGS)

    def report(self, output: CommandOutput, ended_at: datetime) -> ReaderReport | None:
        reader = self.readers.found(output.watch_reader)
        files = OutputFiles(Path(output.folder))
        if reader is None or reader.script or self.readers.is_locked(reader.name) or not files.is_stored() or reader.commands.programs and not self.is_shown_run(reader.commands.read_part(output.command)):
            return None
        lines = self.read_lines(reader, files)
        candidates = [*self.poor_lines(reader, output, lines), *self.single_word_lines(reader, output, lines), *self.progress_findings(reader, output, lines, ended_at), *self.counted_suites(reader, output, lines), *self.missing_summary(reader, output, lines), *self.missing_summary_reader(reader, output, lines, ended_at), *self.mixed_title(reader, output), *self.missing_total(lines)]
        kinds = self.dismissal_kinds(output.command, ended_at)
        shortfalls = [shortfall for shortfall in candidates if not any(kind in shortfall[0] for kind in kinds)]
        if not shortfalls:
            return None
        return ReaderReport(environment_id=output.environment_id, reader=reader.name, output=output.id, command=output.command, session=output.session, findings=tuple(shortfall[0] for shortfall in shortfalls), fixes=tuple(shortfall[1] for shortfall in shortfalls))

    def one_word_title_report(self, output: CommandOutput, title: str) -> ReaderReport | None:
        if self.reports.open_with_output_finding(output.id, SINGLE_WORD_TITLE) or GitCommands.is_git(CommandShape.command_name(Alias.resolved(output.command, self.aliases.index()))):
            return None
        reader = output.watch_reader
        return ReaderReport(environment_id=output.environment_id, reader=reader, output=output.id, command=output.command, session=output.session, findings=(f'{SINGLE_WORD_TITLE}: "{title}"',), fixes=("give the reader a label that says what runs, such as 'Running the rename tool', and a --topic that names it: journal reader add " + (reader or "<name>") + " --label ... --topic ...",))

    def dismissal_kinds(self, command: str, time: datetime) -> set[str]:
        limit = self.settings.integer(ShellOptions.DISMISSAL_LIMIT)
        if not limit:
            return set()
        name = CommandShape.command_name(command)
        reports = self.reports.dismissed_reports(time - timedelta(hours=self.settings.integer(ShellOptions.PAUSE_HOURS)))
        counts = Counter(kind for report in reports if CommandShape.command_name(report.command) == name for kind in self.kinds(report))
        return {kind for kind, count in counts.items() if count >= limit}

    # a dismissal of a finding already dismissed for the same command, and not yet judged sound, waits: the same report coming back
    # means its cause is still there
    def unjudged_dismissal(self, report: ReaderReport, time: datetime) -> ReaderReport | None:
        name, kinds = CommandShape.command_name(report.command), self.kinds(report)
        dismissed = self.reports.dismissed_reports(time - timedelta(hours=self.settings.integer(ShellOptions.PAUSE_HOURS)))
        return next((dismissed_report for dismissed_report in dismissed if dismissed_report.id != report.id and dismissed_report.judged_at is None and CommandShape.command_name(dismissed_report.command) == name and kinds & self.kinds(dismissed_report)), None)

    @staticmethod
    def kinds(report: ReaderReport) -> set[str]:
        return {kind for kind in FINDING_KINDS if any(kind in finding for finding in report.findings)}

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

    def progress_findings(self, reader: Reader, output: CommandOutput, lines: list[str], ended_at: datetime) -> list[tuple[str, str]]:
        if self.is_silent_run(output):
            return []
        return [*self.missing_progress(reader, output, lines, ended_at), *self.late_progress(reader, output, lines, ended_at), *self.unshown_build(reader, output, lines, ended_at), *self.stalled_progress(output)]

    # a run that printed nothing for a stretch was its command's buffering, told to the agent while it ran: no reader can show it, so its progress is not the reader's to answer for
    def is_silent_run(self, output: CommandOutput) -> bool:
        return self.silences.longest_seconds(output.row_id) > STALL_SECONDS

    def late_progress(self, reader: Reader, output: CommandOutput, lines: list[str], ended_at: datetime) -> list[tuple[str, str]]:
        seconds = (ended_at - output.creation_time).total_seconds()
        if seconds < PROGRESS_SECONDS or not reader.progress(lines).is_known() or self.stalls.has_seen(output.row_id):
            return []
        return [(f"the run took {seconds:.0f} seconds and {PROGRESS_LATE}, never while it ran", f"make the run print its count as it goes, N of M as each step finishes, such as scripts/suite.py does for a scoped run: {self.progress_fix(output.command, lines)}")]

    def unshown_build(self, reader: Reader, output: CommandOutput, lines: list[str], ended_at: datetime) -> list[tuple[str, str]]:
        seconds = (ended_at - output.creation_time).total_seconds()
        if self.labels.line_label(output.command) != "building" or seconds < PROGRESS_SECONDS or self.stalls.has_seen(output.row_id) or reader.progress(lines).is_known() or self.has_progress(lines):
            return []
        return [(f"the build ran {seconds:.0f} seconds and {BUILD_UNSHOWN}", f"fix the reader or the command, the journal does not change the reader itself: {StreamingForm.advice(output.command)}")]

    def stalled_progress(self, output: CommandOutput) -> list[tuple[str, str]]:
        seconds = self.stalls.longest_seconds(output.row_id)
        if seconds <= STALL_SECONDS or self.stalls.change_count(output.row_id) >= REGULAR_PROGRESS_CHANGES:
            return []
        return [(f"{PROGRESS_STALLED} {seconds:.0f} seconds while the run went on", "make the run print its progress as it goes, not only when a part of it ends, or give the reader a --progress pattern that picks a figure printed more often")]

    def counted_suites(self, reader: Reader, output: CommandOutput, lines: list[str]) -> list[tuple[str, str]]:
        steps = reader.progress(lines).total
        if not self.processes.counts_suites(output.row_id, steps):
            return []
        inner = self.processes.inner_command(output.row_id) or output.command
        count = self.processes.test_count(output.row_id)
        return [(f"{SUITES_COUNTED}: it shows {steps} steps, and {count} test processes ran beneath {inner}, each running many tests", f"split the output so each test, or each package, prints on its own line with a count against the total: {StreamingForm.advice(inner)}")]

    @staticmethod
    def has_progress(lines: list[str]) -> bool:
        return CountForms.has_total(lines)

    def missing_summary(self, reader: Reader, output: CommandOutput, lines: list[str]) -> list[tuple[str, str]]:
        if reader.variant(output.stage()).card_lines(lines) or not lines:
            return []
        return [(f"{SUMMARY_MISSING}; the run's last line was \"{lines[-1][:120]}\"", "give the reader a --finished and a --failed pattern for the summary line, or make the run print one")]

    def missing_summary_reader(self, reader: Reader, output: CommandOutput, lines: list[str], ended_at: datetime) -> list[tuple[str, str]]:
        seconds = (ended_at - output.creation_time).total_seconds()
        if seconds < PROGRESS_SECONDS or reader.has_summary_reader() or not lines:
            return []
        last = next((line for line in reversed(lines) if SUMMARY_PATTERN.search(line)), lines[-1])
        return [(f"the run took {seconds:.0f} seconds and {SUMMARY_READER_MISSING}", f"give the reader a --summary pattern that picks the figures of its summary line, \"{last[:120]}\", in a few words, such as --summary '(\\d+ failed), (\\d+ passed)'")]

    def prints_total(self, output: CommandOutput) -> bool:
        files = OutputFiles(Path(output.folder))
        return files.is_stored() and CountForms.has_total(files.lines())

    @staticmethod
    def missing_total(lines: list[str]) -> list[tuple[str, str]]:
        if not CountForms.lacks_total(lines):
            return []
        return [(f"{TOTAL_MISSING}, so no progress can be worked out", "make the run print its total as well, such as 'collected 40 items' before the first, or a count of a total on each line, 12/40, so the reader can show how far it has come")]

    def mixed_title(self, reader: Reader, output: CommandOutput) -> list[tuple[str, str]]:
        runs = self.history.reader_ended(reader.name, MIXED_RUNS)
        programs = sorted({name.split()[0] for run in runs if (name := CommandShape.command_name(self.read_command(reader, run)))})
        kinds = sorted({kind for run in runs if (kind := self.work_kind(run))})
        if len(programs) < 2 and len(kinds) < 2:
            return []
        kinds_text = f"the programs {', '.join(programs)}" if len(programs) > 1 else f"runs that print {' and '.join(kinds)}"
        return [(f"{MIXED_TITLE}: \"{output.watch_title or reader.label}\" named for {kinds_text}", "narrow the reader's --commands to the one program it reads, and give the other run a reader of its own with a title that says what it does")]

    # the command of the part of a run's chain the reader reads, so a chain that runs git before the install is named for the install
    def read_command(self, reader: Reader, run: CommandOutput) -> str:
        files = OutputFiles(Path(run.folder))
        read = [files.part_text(i) for i in files.recorded() if reader.commands.reads(files.part_text(i))] if files.is_stored() else []
        return read[0] if read else Alias.resolved(run.command, self.aliases.index())

    @staticmethod
    def work_kind(run: CommandOutput) -> str:
        files = OutputFiles(Path(run.folder))
        lines = files.lines() if files.is_stored() else []
        if any(TEST_TOTALS.search(line) for line in lines):
            return "test totals"
        return "a build line" if any(BUILD_LINE.search(line) for line in lines) else ""

    # the lines of the parts of a chain the reader reads; the whole output when it names no command a part runs
    @staticmethod
    def read_lines(reader: Reader, files: OutputFiles) -> list[str]:
        read = [i for i in files.recorded() if reader.commands.reads(files.part_text(i))]
        if not read:
            return files.lines()
        return [STYLE_CODES.sub("", line) for i in read for line in files.output_text(i).splitlines()]

    def misses(self, reader: Reader, lines: list[str]) -> list[str]:
        misses = []
        if lines and not any(reader.variant(stage).card_lines(lines) for stage in (ACTIVE, FINISHED, FAILED)):
            misses.append(f"it picks no line of the run, whose last lines were {self.quoted(lines[-QUOTED_LINES:])}")
        if CountForms.has_total(lines) and not reader.progress(lines).is_known():
            misses.append(f"it shows no progress, though the run printed {self.quoted(CountForms.progress_lines(lines)[-QUOTED_LINES:])}: {self.progress_fix('', lines)}")
        summary = next((line for line in reversed(lines) if SUMMARY_PATTERN.search(line)), "")
        if summary and summary not in reader.variant(FINISHED).card_lines(lines):
            misses.append(f"it does not end on a line of its own, though the run printed the summary {self.quoted([summary])}: give it a --finished pattern that picks it")
        return [*misses, *self.false_progress(reader, lines)]

    # a count of a total read from figures that are no count, such as the card numbers inside product names, draws a bar that lies
    def false_progress(self, reader: Reader, lines: list[str]) -> list[str]:
        if reader.script or not reader.is_counting():
            return []
        groups = re.compile(reader.progress_pattern).groups
        if groups == 1:
            return self.false_percentage(reader, lines)
        if groups != 2:
            return []
        figures = CountForms.figures(reader.progress_pattern, lines)
        if figures and CountForms.is_count_series(figures) and max(total for _, total in figures) > LARGEST_TOTAL:
            return [f"its --progress counts towards a total of {max(total for _, total in figures)}, {', '.join(f'{count}/{total}' for count, total in figures[:QUOTED_LINES])}: no run does that much work, so the second figure is a number such as an id; give it a pattern for the run's own count, or none, and the card shows how long the run has gone"]
        if not figures or CountForms.is_count_series(figures):
            return []
        shown = [line for line in lines if reader.is_progress_line(line)][:QUOTED_LINES]
        return [f"its --progress selects figures that count towards no total, {', '.join(f'{count}/{total}' for count, total in figures[:QUOTED_LINES])}, in {self.quoted(shown)}: a count of a total never passes its total and shares it from line to line; give it a pattern for the run's own count, or none"]

    def false_percentage(self, reader: Reader, lines: list[str]) -> list[str]:
        large_values = [value for value in CountForms.percentages(reader.progress_pattern, lines) if value > 100]
        if not large_values:
            return []
        return [f"its --progress has one group, which is read as a percentage, and it caught {', '.join(map(str, large_values[:QUOTED_LINES]))}, past 100, so the bar sat full: give it two groups for a count of a total, such as (\\d+)/(\\d+), or none, and the card shows how long the run has gone"]

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
        lines = self.read_lines(reader, files)
        fixes = []
        progress_unshown = any(PROGRESS_MISSING in finding for finding in report.findings) and not reader.progress(lines).is_known() and self.has_progress(lines)
        if progress_unshown:
            fixes.append(self.progress_fix(output.command, lines))
        if any(TOTAL_MISSING in finding for finding in report.findings) and CountForms.lacks_total(lines):
            fixes.append(f"{TOTAL_MISSING}: make it print its total as well, so the reader can work out how far it has come")
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
        form = CountForms.form(lines)
        if form is not None:
            return form.advice
        return StreamingForm.advice(command)
