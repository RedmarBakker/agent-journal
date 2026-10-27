import re

from journal.features.shell.support.count_forms import PERCENT_PATTERN, CountForms
from journal.features.shell.support.reader import Reader
from journal.features.shell.support.reader_commands import ReaderCommands
from journal.features.shell.support.reader_judge import SUMMARY_PATTERN
from journal.features.shell.support.starting_reader import StartingReader
from journal.support.classification import Classification

PERCENT_PROGRESS = r"(\d+)%"
# a summary any run may end on, which every kind's summary pattern takes
SUMMARY = SUMMARY_PATTERN.pattern
# the starting reader of each kind of run the classifier names, a long process being any other run moved to the background
KINDS = {
    "test run": StartingReader("Running tests", failures=r"(?i:\b(?:FAILED|FAIL|ERROR)\b|\bTraceback\b|\bfailed\b|\berror:)", summary=f"(?i:{SUMMARY})"),
    "build": StartingReader("Building", failures=r"(?i:\berror\b|\bfailed\b)", summary=rf"(?i:{SUMMARY}|\bbuilt in\b|\bbuild (?:successful|failed)\b|\bfinished\b|\bcompiled\b|\bdone in\b)"),
    "package": StartingReader("Installing", failures=r"(?i:\berr!|\berror\b)", summary=rf"(?i:{SUMMARY}|\badded \d+ packages?\b|\bsuccessfully installed\b|\bup to date\b|\binstalled\b)"),
}
LONG_PROCESS = StartingReader("Running", failures=r"(?i:\berror\b|\bexception\b|\btraceback\b)", summary=f"(?i:{SUMMARY})", notable=r"(?i:\bwarn(?:ing)?\b|\blistening\b|\bready\b|\bstarted\b)")
# the kinds of a long process, a run moved to the background that is no test run, build or install
LONG_PROCESS_KINDS = frozenset({"process", "unknown"})


class StartingReaders:
    """The reader a run moved to the background starts from, chosen by the kind its classification names, a test run, a build, a package install or a long process, none for a search, a read, version control or the journal's own commands, and filled from the run's own output: the lines of each kind it holds, its progress, its summary and its failures."""

    @staticmethod
    def starting(classification: Classification) -> StartingReader | None:
        return KINDS.get(classification.kind) or (LONG_PROCESS if classification.kind in LONG_PROCESS_KINDS else None)

    def filled(self, classification: Classification, name: str, lines: list[str]) -> Reader | None:
        kind_reader = self.starting(classification)
        patterns = kind_reader.picked(lines) if kind_reader is not None else []
        if not patterns:
            return None
        progress, step_pattern = self.progress_patterns(lines)
        return Reader(re.sub(r"[^a-z0-9]+", "-", f"{name} output".lower()).strip("-"), f"the {kind_reader.label.lower()} lines of {name} runs, written from a run's own output", "|".join(f"(?:{pattern})" for pattern in patterns),
                      progress_pattern=progress, label=kind_reader.label, commands=ReaderCommands((name,)), step_pattern=step_pattern, finished_pattern=kind_reader.summary_pattern(lines), failed_pattern=kind_reader.failure_pattern(lines))

    @staticmethod
    def progress_patterns(lines: list[str]) -> tuple[str, str]:
        if any(PERCENT_PATTERN.search(line) for line in lines):
            return PERCENT_PROGRESS, ""
        form = CountForms.form(lines)
        return (form.progress, form.step) if form else ("", "")
