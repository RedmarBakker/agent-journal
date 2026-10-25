import re
from pathlib import Path

from journal.features.shell.support.output_files import OutputFiles
from journal.features.shell.support.reader import Reader
from journal.features.shell.support.reader_commands import ReaderCommands
from journal.features.shell.support.count_forms import PERCENT_PATTERN, CountForms
from journal.features.shell.support.reader_judge import SUMMARY_PATTERN, ReaderJudge
from journal.features.shell.support.readers import Readers
from journal.models.command_output import CommandOutput
from journal.support.command_shape import CommandShape

PERCENT_PROGRESS = r"(\d+)%"
FAILURE_PATTERN = re.compile(r"\b(?:FAILED|FAIL|ERROR|Traceback)\b|\bfailed\b|\berror:", re.IGNORECASE)


class ReaderGuess:
    """The reader a command moved to the background gets when no reader reads it: a reader of the same program that picks lines from the run's output so far, else one written by code from that output, its progress line, its summary line and its failure lines; kept as a reader of the project, tried on the output before it is offered."""

    def __init__(self, readers: Readers, judge: ReaderJudge) -> None:
        self.readers, self.judge = readers, judge

    def guessed(self, output: CommandOutput, part: str) -> Reader | None:
        files = OutputFiles(Path(output.folder))
        lines = files.lines() if files.is_stored() else []
        name = CommandShape.command_name(part)
        if not lines or not name:
            return None
        reader = self.similar(name, lines) or self.built(name, lines)
        if reader is None or self.judge.misses(reader, lines):
            return None
        if self.readers.stored_reader(reader.name) is None:
            self.readers.add(reader)
        return self.readers.stored_reader(reader.name)

    def similar(self, name: str, lines: list[str]) -> Reader | None:
        program = name.split()[0]
        return next((reader for reader in self.readers.all() if any(program_text.split()[0] == program for program_text in reader.commands.programs) and not self.judge.misses(reader, lines)), None)

    @staticmethod
    def progress_patterns(lines: list[str]) -> tuple[str, str]:
        if any(PERCENT_PATTERN.search(line) for line in lines):
            return PERCENT_PROGRESS, ""
        form = CountForms.form(lines)
        return (form.progress, form.step) if form else ("", "")

    def built(self, name: str, lines: list[str]) -> Reader | None:
        progress, step = self.progress_patterns(lines)
        summary = f"(?i:{SUMMARY_PATTERN.pattern})" if any(SUMMARY_PATTERN.search(line) for line in lines) else ""
        failures = f"(?i:{FAILURE_PATTERN.pattern})" if any(FAILURE_PATTERN.search(line) for line in lines) else ""
        patterns = [pattern for pattern in (failures, summary) if pattern]
        if not patterns:
            return None
        subject = " and ".join(word for word, present in (("progress", progress), ("failure lines", failures), ("summary", summary)) if present)
        return Reader(re.sub(r"[^a-z0-9]+", "-", f"{name} output".lower()).strip("-"), f"the {subject} of {name} runs, written from a run's own output", "|".join(f"(?:{pattern})" for pattern in patterns),
                      progress_pattern=progress, step_pattern=step, commands=ReaderCommands((name,)), finished_pattern=summary, failed_pattern=failures)
